"""
Generate grant data for grant_agent.
Run from project root:
uv run python app/agent/manager/sub_agent/grant_agent/scripts/generate_grant_data.py
"""
import json
import random
import uuid
from datetime import date, timedelta
from pathlib import Path
from faker import Faker

Faker.seed(42)
random.seed(42)
fake = Faker()

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

PLANS = [
    {"plan_id": "PLAN-001",
     "plan_name": "2020 Equity Incentive Plan",
     "plan_type": "Omnibus",
     "pool_size": 500000},
    {"plan_id": "PLAN-002",
     "plan_name": "2022 Performance Share Plan",
     "plan_type": "Performance",
     "pool_size": 250000},
    {"plan_id": "PLAN-003",
     "plan_name": "2024 Stock Option Plan",
     "plan_type": "Option",
     "pool_size": 150000},
]

GRANT_TYPES        = ["RSU", "RSU", "PSU", "Stock Option"]
SCHEDULES          = ["4-year monthly", "3-year quarterly", "4-year annual"]
CLIFF_MONTHS       = {"4-year monthly": 12, "3-year quarterly": 12,
                      "4-year annual": 12}
STATUSES           = ["Active", "Active", "Active", "Cancelled", "Expired"]
PERF_CONDITIONS    = [None, None, None,
                      "TSR ranking top 50%",
                      "Revenue growth > 10%",
                      "EPS target achieved"]

def make_grant(employee_id, employee_name, plan):
    grant_type  = random.choice(GRANT_TYPES)
    schedule    = random.choice(SCHEDULES)
    cliff       = CLIFF_MONTHS[schedule]
    grant_date  = fake.date_between(start_date="-5y", end_date="-1y")
    expiry_date = grant_date + timedelta(days=365 * 8)
    total       = random.randint(500, 5000)
    pct_vested  = round(random.uniform(0.1, 0.9), 2)
    vested      = int(total * pct_vested)
    unvested    = total - vested
    price_at_grant = round(random.uniform(20.0, 200.0), 2)
    grant_value = round(total * price_at_grant, 2)
    status      = random.choice(STATUSES)
    perf        = random.choice(PERF_CONDITIONS)
    grant_id    = f"GR-{uuid.uuid4().hex[:8].upper()}-{fake.bothify('???').upper()}"

    return {
        "grant_id":                  grant_id,
        "employee_id":               employee_id,
        "employee_name":             employee_name,
        "plan_id":                   plan["plan_id"],
        "plan_name":                 plan["plan_name"],
        "grant_type":                grant_type,
        "grant_date":                grant_date.isoformat(),
        "expiry_date":               expiry_date.isoformat(),
        "total_shares_granted":      total,
        "vested_shares":             vested,
        "unvested_shares":           unvested,
        "percentage_vested":         round(pct_vested * 100, 1),
        "grant_value_at_grant_date": grant_value,
        "vesting_schedule":          schedule,
        "cliff_months":              cliff,
        "performance_conditions":    perf,
        "grant_status":              status,
    }

def main():
    grants = []
    for emp_id, emp_name in EMPLOYEES:
        plan = random.choice(PLANS)
        for _ in range(random.randint(2, 3)):
            grants.append(make_grant(emp_id, emp_name, plan))

    output = {"plans": PLANS, "grants": grants}
    out_path = (Path(__file__).parent.parent
                / "grant_data" / "grants.json")
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))
    print(f"Generated {len(grants)} grants -> {out_path}")

if __name__ == "__main__":
    main()
