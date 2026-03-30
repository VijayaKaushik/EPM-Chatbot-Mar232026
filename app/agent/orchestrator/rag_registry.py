"""
RAG Agent Registry.
Add new RAG agents here — zero changes needed anywhere else.
Planner reads this registry to build routing rules dynamically.
"""

RAG_AGENTS = {
    "user_guide_agent": {
        "description": (
            "Generic application how-to questions, concept explanations, "
            "app navigation, step-by-step procedures, best practices. "
            "Covers simulation, vesting schedule view, KYC process, "
            "dashboard navigation, profile updates, release approval steps."
        ),
        "triggers": [
            "how do I", "what is", "steps to", "explain",
            "guide me", "what does", "best practices",
            "how to", "where do I", "navigate",
        ],
        "topics": [
            "release simulation", "vesting schedule", "KYC process",
            "dashboard", "profile update", "release approval",
            "grant viewing", "release history", "login", "access",
        ],
        "excludes": [
            "contacts", "SLA", "CRM", "client policy",
            "escalation", "EPM lead", "terminated policy",
        ],
    },
    "client_ops_agent": {
        "description": (
            "Client-specific operational questions. CRM contacts, "
            "EPM team contacts, escalation SLAs, client-specific "
            "how-to procedures, terminated employee policy, "
            "client compliance requirements. "
            "Client determined by client_id in session state."
        ),
        "triggers": [
            "contact", "CRM", "escalation", "SLA", "EPM lead",
            "terminated policy", "client compliance", "who is",
            "how long does", "client specific", "orion", "our client",
        ],
        "topics": [
            "CRM contacts", "EPM contacts", "escalation SLA",
            "termination policy", "client compliance",
            "address change process", "email change process",
            "audit requirements", "data privacy",
        ],
        "excludes": [
            "how do I navigate", "steps to simulate",
            "what is vesting", "what is KYC concept",
        ],
    },
}


def get_rag_agent_names() -> list[str]:
    """Returns list of all registered RAG agent names."""
    return list(RAG_AGENTS.keys())


def get_rag_routing_description() -> str:
    """
    Builds dynamic RAG routing description for planner prompt.
    Called at planner startup — auto-updates as agents are added.
    """
    lines = ["## Registered RAG Agents\n"]
    for agent_name, config in RAG_AGENTS.items():
        lines.append(f"### {agent_name}")
        lines.append(f"Description: {config['description']}")
        lines.append(f"Route here when query mentions: {', '.join(config['triggers'])}")
        lines.append(f"Topics covered: {', '.join(config['topics'])}")
        if config["excludes"]:
            lines.append(f"Do NOT route here for: {', '.join(config['excludes'])}")
        lines.append("")
    return "\n".join(lines)


def is_rag_agent(agent_name: str) -> bool:
    """Check if a given agent name is a registered RAG agent."""
    return agent_name in RAG_AGENTS
