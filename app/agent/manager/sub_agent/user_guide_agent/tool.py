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

DOCS_DIR   = pathlib.Path(__file__).parent / "docs"
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 100


def _extract_text_from_pdfs() -> List[Dict]:
    """
    Reads all PDFs from docs/ folder.
    Returns list of chunks with metadata.
    Each chunk: {text, source, page, chunk_index}
    """
    chunks = []
    chunk_index = 0

    for pdf_path in sorted(DOCS_DIR.glob("*.pdf")):
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


async def build_index(tool_context: ToolContext) -> Dict:
    """
    Builds FAISS index from all PDFs in docs/ folder.
    Saves index and chunk metadata to ADK artifacts.
    Only needs to be called once per session or when new PDFs are added.
    Subsequent calls load from artifact automatically.

    LLM Prompt Examples:
      - "Initialize the knowledge base"
      - "Build the search index"
      - Called automatically before search_guides if artifact missing
    """
    try:
        existing = await tool_context.load_artifact("user_guide_index.pkl")
        if existing:
            chunks_artifact = await tool_context.load_artifact("user_guide_chunks.json")
            chunks = json.loads(chunks_artifact.text)
            print(f"\n📚 BUILD_INDEX source: artifact | chunks: {len(chunks)}\n")
            return {
                "status":       "success",
                "source":       "artifact",
                "total_chunks": len(chunks),
                "documents":    list(set(c["source"] for c in chunks)),
                "message":      "Index already built — loaded from artifact"
            }
    except Exception:
        pass

    print(f"\n📚 BUILD_INDEX source: disk — building new index\n")

    api_key = os.environ.get("GOOGLE_API_KEY", "")

    chunks = _extract_text_from_pdfs()
    if not chunks:
        return {
            "status":  "error",
            "message": "No PDF documents found in docs/ folder"
        }

    texts      = [c["text"] for c in chunks]
    embeddings = _get_embeddings(texts, api_key)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    index_bytes = pickle.dumps(index)

    try:
        await tool_context.save_artifact(
            filename="user_guide_index.pkl",
            artifact=genai_types.Part(
                inline_data=genai_types.Blob(
                    data=index_bytes,
                    mime_type="application/octet-stream"
                )
            )
        )
        await tool_context.save_artifact(
            filename="user_guide_chunks.json",
            artifact=genai_types.Part(text=json.dumps(chunks))
        )
    except Exception as e:
        print(f"\n⚠️  BUILD_INDEX artifact save failed: {e} — index held in memory only\n")

    documents = list(set(c["source"] for c in chunks))
    return {
        "status":       "success",
        "source":       "disk",
        "total_chunks": len(chunks),
        "documents":    documents,
        "message":      f"Index built from {len(documents)} documents, {len(chunks)} chunks"
    }


async def search_guides(
    query: str,
    tool_context: ToolContext,
    top_k: int = 3,
) -> Dict:
    """
    Searches user guide documents using semantic similarity.
    Loads FAISS index from artifact — no disk read after first build.
    Returns answer synthesized from top matching chunks,
    with source section and suggested next action in the app.

    Args:
        query: Natural language question about the application
        top_k: Number of chunks to retrieve (default 3)

    LLM Prompt Examples:
      - "How do I simulate a release?"
      - "What is KYC and how do I complete it?"
      - "How do I view my vesting schedule?"
      - "What does the dashboard show?"
      - "How do I update my profile?"
      - "What are the steps to approve a release?"
      - "How do I track vesting dates?"
      - "What is a grant?"
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "")

    index  = None
    chunks = None

    try:
        index_artifact  = await tool_context.load_artifact("user_guide_index.pkl")
        chunks_artifact = await tool_context.load_artifact("user_guide_chunks.json")
        if index_artifact and chunks_artifact:
            index  = pickle.loads(index_artifact.inline_data.data)
            chunks = json.loads(chunks_artifact.text)
            print(f"\n🔍 SEARCH_GUIDES source: artifact | query: {query}\n")
    except Exception:
        pass

    if index is None or chunks is None:
        print(f"\n🔍 SEARCH_GUIDES — no artifact, building index from disk\n")
        build_result = await build_index(tool_context)
        if build_result["status"] != "success":
            return {
                "status":  "error",
                "query":   query,
                "message": "Failed to build index from documents"
            }
        # Rebuild in-memory from disk directly (artifact may be unavailable)
        chunks = _extract_text_from_pdfs()
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
            "status":  "not_found",
            "query":   query,
            "message": "No relevant content found for this query"
        }

    context = "\n\n".join([
        f"[Source: {c['source']}, Page {c['page']}]\n{c['text']}"
        for c in matched_chunks
    ])

    client = genai.Client(api_key=api_key)
    synthesis_prompt = f"""
You are a helpful assistant for an equity plan management application.
Answer the user's question based ONLY on the provided documentation context.
After your answer, suggest the specific next action the user should take in the app.

Documentation context:
{context}

User question: {query}

Respond in this format:
ANSWER: [your answer based on the documentation]
SOURCE: [which document and section this came from]
NEXT ACTION: [specific step the user should take in the app]
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=synthesis_prompt,
    )

    return {
        "status":      "success",
        "source":      "artifact",
        "query":       query,
        "answer":      response.text,
        "chunks_used": len(matched_chunks),
        "sources":     [f"{c['source']} p.{c['page']}" for c in matched_chunks],
        "message":     "Answer synthesized from documentation"
    }


async def list_topics(tool_context: ToolContext) -> Dict:
    """
    Lists all available document sections in the knowledge base.
    Loads from artifact — no disk read after first build.
    Used when user asks what topics are available.

    LLM Prompt Examples:
      - "What can you help me with?"
      - "What topics are covered?"
      - "What documents do you have?"
      - "Show me available guides"
    """
    chunks = None

    try:
        chunks_artifact = await tool_context.load_artifact("user_guide_chunks.json")
        if chunks_artifact:
            chunks = json.loads(chunks_artifact.text)
            print(f"\n📋 LIST_TOPICS source: artifact\n")
    except Exception:
        pass

    if chunks is None:
        print(f"\n📋 LIST_TOPICS — no artifact, loading from disk\n")
        await build_index(tool_context)
        chunks = _extract_text_from_pdfs()

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
            "pages_covered": sorted(info["pages"])
        }
        for src, info in documents.items()
    }

    return {
        "status":    "success",
        "source":    "artifact",
        "documents": doc_summary,
        "message":   f"Knowledge base contains {len(documents)} documents"
    }
