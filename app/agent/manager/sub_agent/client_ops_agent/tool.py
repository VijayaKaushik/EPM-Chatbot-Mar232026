import json
import os
import pathlib
import pickle
from typing import Dict, List, Optional

import faiss
import numpy as np
from google.adk.tools.tool_context import ToolContext
from google.genai import types as genai_types
from google import genai
from PyPDF2 import PdfReader

DOCS_BASE_DIR = pathlib.Path(__file__).parent / "docs"
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 100


def _get_client_docs_dir(client_id: str) -> pathlib.Path:
    """Returns the docs folder for a specific client."""
    return DOCS_BASE_DIR / client_id


def _get_index_artifact_key(client_id: str) -> str:
    return f"client_ops_index_{client_id}.pkl"


def _get_chunks_artifact_key(client_id: str) -> str:
    return f"client_ops_chunks_{client_id}.json"


def _extract_text_from_pdfs(client_id: str) -> List[Dict]:
    """
    Reads all PDFs from docs/{client_id}/ folder.
    Returns list of chunks with metadata.
    Each chunk: {text, source, page, chunk_index, client_id}
    """
    chunks = []
    chunk_index = 0
    docs_dir = _get_client_docs_dir(client_id)

    for pdf_path in sorted(docs_dir.glob("*.pdf")):
        reader = PdfReader(str(pdf_path))
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            start = 0
            while start < len(text):
                end = start + CHUNK_SIZE
                chunk_text = text[start:end]
                if chunk_text.strip():
                    chunks.append({
                        "text":        chunk_text.strip(),
                        "source":      pdf_path.name,
                        "page":        page_num + 1,
                        "chunk_index": chunk_index,
                        "client_id":   client_id,
                    })
                    chunk_index += 1
                start = end - CHUNK_OVERLAP

    return chunks


def _get_embeddings(texts: List[str], api_key: str) -> np.ndarray:
    """Generate embeddings using Gemini embedding model."""
    client = genai.Client(api_key=api_key)
    embeddings = []
    for text in texts:
        response = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text,
        )
        embeddings.append(response.embeddings[0].values)
    return np.array(embeddings, dtype=np.float32)


async def build_client_index(tool_context: ToolContext) -> dict:
    """
    Builds FAISS index from all PDFs in docs/{client_id}/ folder.
    Saves index and chunks to ADK artifacts keyed by client_id.
    Reads client_id from session state.
    Only needs to be called once per session per client.

    LLM Prompt Examples:
      - "Initialize client knowledge base"
      - Called automatically before search_client_docs if artifact missing
    """
    client_id  = tool_context.state.get("client_id", "CLIENT-001")
    index_key  = _get_index_artifact_key(client_id)
    chunks_key = _get_chunks_artifact_key(client_id)

    try:
        existing = await tool_context.load_artifact(index_key)
        if existing:
            chunks_artifact = await tool_context.load_artifact(chunks_key)
            chunks = json.loads(chunks_artifact.text)
            print(f"\n📚 BUILD_CLIENT_INDEX client: {client_id} source: artifact | chunks: {len(chunks)}\n")
            return {
                "status":       "success",
                "source":       "artifact",
                "client_id":    client_id,
                "total_chunks": len(chunks),
                "documents":    list(set(c["source"] for c in chunks)),
                "message":      "Index already built — loaded from artifact",
            }
    except Exception:
        pass

    print(f"\n📚 BUILD_CLIENT_INDEX client: {client_id} source: disk — building new index\n")

    docs_dir = _get_client_docs_dir(client_id)
    if not docs_dir.exists():
        return {
            "status":  "error",
            "client_id": client_id,
            "message": f"No documents found for client {client_id}",
        }

    api_key = os.environ.get("GOOGLE_API_KEY", "")

    chunks = _extract_text_from_pdfs(client_id)
    if not chunks:
        return {
            "status":    "error",
            "client_id": client_id,
            "message":   f"No PDF documents found for client {client_id}",
        }

    texts      = [c["text"] for c in chunks]
    embeddings = _get_embeddings(texts, api_key)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    index_bytes = pickle.dumps(index)

    try:
        await tool_context.save_artifact(
            filename=index_key,
            artifact=genai_types.Part(
                inline_data=genai_types.Blob(
                    data=index_bytes,
                    mime_type="application/octet-stream",
                )
            )
        )
        await tool_context.save_artifact(
            filename=chunks_key,
            artifact=genai_types.Part(text=json.dumps(chunks))
        )
    except Exception as e:
        print(f"\n⚠️  BUILD_CLIENT_INDEX artifact save failed: {e} — index held in memory only\n")

    documents = list(set(c["source"] for c in chunks))
    return {
        "status":       "success",
        "source":       "disk",
        "client_id":    client_id,
        "total_chunks": len(chunks),
        "documents":    documents,
        "message":      f"Index built from {len(documents)} documents, {len(chunks)} chunks",
    }


async def search_client_docs(
    query: str,
    tool_context: ToolContext,
    top_k: int = 3,
) -> dict:
    """
    Searches client-specific documentation using semantic similarity.
    Reads client_id from session state.
    Loads FAISS index from artifact — no disk read after first build.
    Returns answer with source section and suggested next action.

    Args:
        query: Natural language question about client-specific operations

    LLM Prompt Examples:
      - "Who is the CRM contact for this client?"
      - "What is the escalation SLA for critical issues?"
      - "How does this client handle terminated employees?"
      - "What are the compliance requirements?"
      - "How do I change address for this client?"
      - "Who is the EPM lead for this client?"
      - "What CRM system does this client use?"
    """
    client_id  = tool_context.state.get("client_id", "CLIENT-001")
    index_key  = _get_index_artifact_key(client_id)
    chunks_key = _get_chunks_artifact_key(client_id)
    api_key    = os.environ.get("GOOGLE_API_KEY", "")

    index  = None
    chunks = None

    try:
        index_artifact  = await tool_context.load_artifact(index_key)
        chunks_artifact = await tool_context.load_artifact(chunks_key)
        if index_artifact and chunks_artifact:
            index  = pickle.loads(index_artifact.inline_data.data)
            chunks = json.loads(chunks_artifact.text)
            print(f"\n🔍 SEARCH_CLIENT_DOCS client: {client_id} source: artifact | query: {query}\n")
    except Exception:
        pass

    if index is None or chunks is None:
        print(f"\n🔍 SEARCH_CLIENT_DOCS client: {client_id} — no artifact, building index from disk\n")
        build_result = await build_client_index(tool_context)
        if build_result["status"] != "success":
            return {
                "status":    "error",
                "client_id": client_id,
                "query":     query,
                "message":   f"Failed to build index for client {client_id}",
            }
        chunks = _extract_text_from_pdfs(client_id)
        texts  = [c["text"] for c in chunks]
        embeddings = _get_embeddings(texts, api_key)
        dimension  = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

    query_embedding = _get_embeddings([query], api_key)
    distances, indices = index.search(query_embedding, top_k)

    matched_chunks = [
        chunks[idx] for idx in indices[0] if idx < len(chunks)
    ]

    if not matched_chunks:
        return {
            "status":    "not_found",
            "client_id": client_id,
            "query":     query,
            "message":   "No relevant content found for this query",
        }

    context = "\n\n".join([
        f"[Source: {c['source']}, Page {c['page']}]\n{c['text']}"
        for c in matched_chunks
    ])

    client = genai.Client(api_key=api_key)
    synthesis_prompt = f"""
You are a helpful assistant for client {client_id} operations.
Answer the question based ONLY on the provided client documentation.
After your answer, suggest the specific next action if applicable.

Documentation context:
{context}

Question: {query}

Respond in this format:
ANSWER: [answer from documentation]
SOURCE: [document and section]
NEXT ACTION: [specific next step if applicable, or N/A]
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=synthesis_prompt,
    )

    return {
        "status":      "success",
        "source":      "artifact",
        "client_id":   client_id,
        "query":       query,
        "answer":      response.text,
        "chunks_used": len(matched_chunks),
        "sources":     [f"{c['source']} p.{c['page']}" for c in matched_chunks],
        "message":     "Answer synthesized from client documentation",
    }


async def list_client_topics(tool_context: ToolContext) -> dict:
    """
    Lists available topics in client documentation.
    Reads client_id from session state.
    Loads from artifact — no disk read after first build.

    LLM Prompt Examples:
      - "What client information do you have?"
      - "What can you help me with for this client?"
      - "List available client documentation"
    """
    client_id  = tool_context.state.get("client_id", "CLIENT-001")
    chunks_key = _get_chunks_artifact_key(client_id)
    chunks: Optional[List[Dict]] = None

    try:
        chunks_artifact = await tool_context.load_artifact(chunks_key)
        if chunks_artifact:
            chunks = json.loads(chunks_artifact.text)
            print(f"\n📋 LIST_CLIENT_TOPICS client: {client_id} source: artifact\n")
    except Exception:
        pass

    if chunks is None:
        print(f"\n📋 LIST_CLIENT_TOPICS client: {client_id} — no artifact, loading from disk\n")
        await build_client_index(tool_context)
        chunks = _extract_text_from_pdfs(client_id)

    documents = {}
    for chunk in chunks:
        src = chunk["source"]
        if src not in documents:
            documents[src] = {"total_chunks": 0, "pages": set()}
        documents[src]["total_chunks"] += 1
        documents[src]["pages"].add(chunk["page"])

    doc_summary = {
        src: {
            "total_chunks":  info["total_chunks"],
            "pages_covered": sorted(info["pages"]),
        }
        for src, info in documents.items()
    }

    return {
        "status":    "success",
        "source":    "artifact",
        "client_id": client_id,
        "documents": doc_summary,
        "message":   f"Knowledge base for {client_id} contains {len(documents)} documents",
    }
