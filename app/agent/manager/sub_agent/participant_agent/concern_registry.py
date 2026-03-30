"""
Concern Detection Registry.
Add new concern rules here — zero changes needed in tool.py.
Each rule drives automatic detection against participant DataFrame.
To upgrade to LLM-based detection → replace _detect_concerns() in tool.py,
this registry stays unchanged as the source of truth.
"""

CONCERN_RULES = [
    {
        "type":          "kyc_incomplete",
        "description":   "KYC Action Required",
        "severity":      "high",
        "filter_field":  "kyc_status",
        "filter_values": ["Pending", "Expired"],
        "filter_op":     "isin",
        "id_field":      "employee_id",
        "enrich_agent":  "user_guide_agent",
        "enrich_query":  "what should admin do with pending or expired KYC participants",
    },
    {
        "type":          "terminated_employees",
        "description":   "Terminated Employee Policy",
        "severity":      "medium",
        "filter_field":  "employment_status",
        "filter_values": ["Terminated"],
        "filter_op":     "isin",
        "id_field":      "employee_id",
        "enrich_agent":  "client_ops_agent",
        "enrich_query":  "how does this client handle terminated employees with equity grants",
    },
    {
        "type":          "ach_unverified",
        "description":   "ACH Verification Needed",
        "severity":      "medium",
        "filter_field":  "ach_status",
        "filter_values": ["Not Verified"],
        "filter_op":     "isin",
        "id_field":      "employee_id",
        "enrich_agent":  "user_guide_agent",
        "enrich_query":  "how to resolve unverified ACH status for participants",
    },
    {
        "type":          "insider_in_blackout",
        "description":   "Insider Blackout Compliance",
        "severity":      "critical",
        "filter_field":  "insider_status",
        "filter_values": ["Insider"],
        "filter_op":     "isin",
        "also_filter": {
            "field":  "blackout_status",
            "values": ["In Blackout"],
            "op":     "isin",
        },
        "id_field":      "employee_id",
        "enrich_agent":  "client_ops_agent",
        "enrich_query":  "client compliance requirements for insiders in blackout period",
    },
]
