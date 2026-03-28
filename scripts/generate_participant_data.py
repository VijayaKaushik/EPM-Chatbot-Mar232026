"""
Generate sample participant data using Faker.
Outputs two JSON files into app/participant_data/:
  - participants.json        (high-level record per employee)
  - participant_details.json (detailed blobs per employee)

All participants belong to CLIENT-001 (single company).
Employee IDs and names are seeded from the vesting dataset.
"""

import json
import random
from pathlib import Path

from faker import Faker

# ── Seed for reproducibility ──────────────────────────────────────────────────
Faker.seed(42)
random.seed(42)
fake = Faker()

# ── Employee IDs + names from vesting dataset (source of truth) ───────────────
EMPLOYEES = [
    ("74069291", "Taylor Randolph"),
    ("31582740", "Marcus Chen"),
    ("58203617", "Sophia Alvarez"),
    ("90124536", "Priya Sharma"),
    ("44781923", "Derek Olson"),
    ("67320185", "Amara Okafor"),
    ("82910374", "Kenji Watanabe"),
    ("15649208", "Rachel Foster"),
    ("39572061", "Miguel Santos"),
    ("53186740", "Lin Zhang"),
    ("22487163", "Olivia Bennett"),
    ("85631907", "Ibrahim Hassan"),
    ("41893256", "Hannah Johansson"),
    ("28764091", "David Moreau"),
    ("72450318", "Elena Petrova"),
]

CLIENT_ID = "CLIENT-001"  # single company

# ── Reference data ────────────────────────────────────────────────────────────
DEPARTMENTS = [
    "Finance", "Engineering", "Sales", "Operations",
    "HR", "Legal", "Marketing",
]
JOB_TITLES = {
    "Finance":     ["Senior Analyst", "Director of Finance", "CFO", "Controller"],
    "Engineering": ["Staff Engineer", "VP Engineering", "Engineering Manager", "Tech Lead"],
    "Sales":       ["Account Executive", "Sales Director", "Regional Manager"],
    "Operations":  ["Operations Lead", "Operations Manager", "Program Manager"],
    "HR":          ["HR Business Partner", "Talent Acquisition Lead", "HR Manager"],
    "Legal":       ["Compliance Officer", "Senior Counsel", "Associate Counsel"],
    "Marketing":   ["Marketing Manager", "Brand Strategist", "Growth Lead"],
}
INSIDER_TITLES = {"CFO", "VP Engineering", "Director of Finance", "Senior Counsel"}

COUNTRIES = [
    "United States", "United States", "United States",   # weighted higher
    "Canada", "United Kingdom", "Germany", "France",
    "Spain", "India", "Australia", "Japan",
    "Brazil", "South Korea", "Sweden", "Netherlands",
]
TAX_RESIDENCY_MAP = {
    "United States":  ("US Resident",        "W9 on file",      0.22),
    "Canada":         ("Canadian Resident",   "W8-BEN on file",  0.25),
    "United Kingdom": ("UK Resident",         "W8-BEN on file",  0.20),
    "Germany":        ("EU Resident",         "W8-BEN on file",  0.26),
    "France":         ("EU Resident",         "W8-BEN on file",  0.28),
    "Spain":          ("EU Resident",         "W8-BEN on file",  0.19),
    "India":          ("Non-US Resident",     "W8-BEN on file",  0.25),
    "Australia":      ("Non-US Resident",     "W8-BEN on file",  0.15),
    "Japan":          ("Non-US Resident",     "W8-BEN on file",  0.20),
    "Brazil":         ("Non-US Resident",     "W8-BEN on file",  0.15),
    "South Korea":    ("Non-US Resident",     "W8-BEN on file",  0.22),
    "Sweden":         ("EU Resident",         "W8-BEN on file",  0.25),
    "Netherlands":    ("EU Resident",         "W8-BEN on file",  0.21),
}
BANKS = {
    "United States":  "Chase",
    "Canada":         "RBC Royal Bank",
    "United Kingdom": "Barclays",
    "Germany":        "Deutsche Bank",
    "France":         "BNP Paribas",
    "Spain":          "Santander",
    "India":          "HDFC Bank",
    "Australia":      "Commonwealth Bank",
    "Japan":          "MUFG Bank",
    "Brazil":         "Itau Unibanco",
    "South Korea":    "KB Kookmin Bank",
    "Sweden":         "Swedbank",
    "Netherlands":    "ING Bank",
}
KYC_STATUSES     = ["Verified", "Verified", "Verified", "Pending", "Expired"]
ACH_STATUSES     = ["Verified", "Verified", "Pending", "Not Verified"]
ACCOUNT_STATUSES = ["Active", "Active", "Active", "Restricted", "Closed"]
BLACKOUT_OPTIONS = ["Not in Blackout", "Not in Blackout", "Not in Blackout", "In Blackout"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_broker_code() -> str:
    return f"BR-{random.randint(100000, 999999)}"


def make_officer_code() -> str:
    return f"OFC-{random.randint(1000, 9999)}"


def make_brokerage_account() -> str:
    return f"BR-ACC-{random.randint(100000, 999999)}"


def make_address(country: str) -> dict:
    return {
        "street":  fake.street_address(),
        "city":    fake.city(),
        "state":   fake.state(),
        "zip":     fake.postcode(),
        "country": country,
    }


# ── Generators ────────────────────────────────────────────────────────────────

def make_participant(employee_id: str, full_name: str) -> dict:
    country     = random.choice(COUNTRIES)
    department  = random.choice(DEPARTMENTS)
    job_title   = random.choice(JOB_TITLES[department])
    emp_status  = random.choices(["Active", "Terminated"], weights=[85, 15])[0]

    insider_status  = (
        "Insider" if job_title in INSIDER_TITLES and emp_status == "Active"
        else "Non-Insider"
    )
    blackout_status = (
        random.choice(BLACKOUT_OPTIONS) if insider_status == "Insider"
        else "Not in Blackout"
    )

    return {
        "employee_id":          employee_id,
        "full_name":            full_name,          # real name from vesting data
        "country_of_residence": country,
        "employment_status":    emp_status,
        "insider_status":       insider_status,
        "blackout_status":      blackout_status,
        "kyc_status":           random.choice(KYC_STATUSES),
        "broker_code":          make_broker_code(),
        "officer_code":         make_officer_code(),
        "client_id":            CLIENT_ID,
        "department":           department,
        "job_title":            job_title,
        "grant_eligible":       emp_status == "Active",
    }


def make_participant_details(
    employee_id: str, country: str, emp_status: str
) -> dict:
    tax_residency, w8_w9, rate = TAX_RESIDENCY_MAP.get(
        country, ("Non-US Resident", "W8-BEN on file", 0.30)
    )
    bank = BANKS.get(country, "International Bank")

    if emp_status == "Terminated":
        acct_status = random.choice(["Closed", "Restricted"])
        ach_status  = "Not Verified"
        office_addr = {
            "street": "N/A", "city": "N/A",
            "state": "N/A",  "zip": "N/A", "country": "N/A",
        }
    else:
        acct_status = random.choice(ACCOUNT_STATUSES)
        ach_status  = random.choice(ACH_STATUSES)
        office_addr = make_address(country)

    return {
        "employee_id":     employee_id,
        "current_address": make_address(country),
        "office_address":  office_addr,
        "tax_info": {
            "tax_id":           f"XXX-XX-{random.randint(1000, 9999)}",
            "tax_country":      country,
            "tax_residency":    tax_residency,
            "withholding_rate": rate,
            "w8_w9_status":     w8_w9,
        },
        "account_info": {
            "brokerage_account": make_brokerage_account(),
            "account_status":    acct_status,
            "account_type":      random.choice(["Individual", "Individual", "Corporate"]),
            "bank_name":         bank,
            "ach_status":        ach_status,
        },
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    #output_dir = Path(__file__).parent.parent / "app" / "participant_data"
    output_dir = Path(__file__).parent.parent / "app" / "agent" / "manager" / "sub_agent" / "participant_agent" / "participant_data"


    output_dir.mkdir(parents=True, exist_ok=True)

    participants        = []
    participant_details = []

    for emp_id, full_name in EMPLOYEES:
        p = make_participant(emp_id, full_name)
        participants.append(p)

        d = make_participant_details(
            emp_id, p["country_of_residence"], p["employment_status"]
        )
        participant_details.append(d)

    p_path = output_dir / "participants.json"
    p_path.write_text(json.dumps(participants, indent=2))
    print(f"✅ Written {len(participants)} records → {p_path}")

    d_path = output_dir / "participant_details.json"
    d_path.write_text(json.dumps(participant_details, indent=2))
    print(f"✅ Written {len(participant_details)} records → {d_path}")

    print("\nEmployee ID → Name mapping:")
    for p in participants:
        print(f"  {p['employee_id']}  {p['full_name']:<20}  "
              f"{p['employment_status']:<12}  {p['country_of_residence']}")


if __name__ == "__main__":
    main()
