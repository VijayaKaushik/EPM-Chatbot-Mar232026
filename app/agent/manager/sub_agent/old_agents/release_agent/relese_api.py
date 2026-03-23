from faker import Faker
import json
from datetime import datetime, timedelta
import random

fake = Faker()


def generate_release_activity(
    num_records=50, release_date="2024-12-15", fmv=None, sale_price=None
):
    """
    Generate equity plan release activity data for a specific vesting/release date
    """

    release_activities = []

    # Parse the release date
    release_dt = datetime.strptime(release_date, "%Y-%m-%d")

    for _ in range(num_records):
        # Generate grant date (1-4 years before release)
        grant_date = release_dt - timedelta(days=random.randint(365, 1460))

        # Calculate shares
        total_granted = random.randint(100, 10000)
        release_percentage = random.choice(
            [25, 33, 50, 100]
        )  # Common vesting percentages
        shares_released = int(total_granted * release_percentage / 100)
        shares_withheld_tax = int(
            shares_released * random.uniform(0.22, 0.37)
        )  # Tax withholding
        net_shares = shares_released - shares_withheld_tax

        # Stock price and values
        stock_price = sale_price
        tax_withheld_value = None
        if sale_price:
            tax_withheld_value = round(shares_withheld_tax * stock_price, 2)

        record = {
            "employee_id": fake.uuid4()[:8].upper(),
            "employee_name": fake.name(),
            "email": fake.email(),
            "department": random.choice(
                [
                    "Engineering",
                    "Sales",
                    "Marketing",
                    "Finance",
                    "Operations",
                    "Product",
                    "HR",
                ]
            ),
            "employee_status": random.choice(
                ["Active", "Active", "Active", "Active", "Terminated"]
            ),  # Mostly active
            "grant_id": f"GR-{fake.uuid4()[:12].upper()}",
            "grant_date": grant_date.strftime("%Y-%m-%d"),
            "grant_type": random.choice(
                ["RSU", "Stock Option", "PSU", "Restricted Stock"]
            ),
            "total_shares_granted": total_granted,
            "vesting_schedule": random.choice(
                ["4-year monthly", "4-year quarterly", "3-year quarterly", "Annual"]
            ),
            "release_date": release_date,
            "release_number": random.randint(1, 16),  # Which vesting period
            "shares_released": shares_released,
            "shares_withheld_for_taxes": shares_withheld_tax,
            "net_shares_delivered": net_shares,
            "stock_price_at_release": stock_price,
            "fmv_at_release": fmv,
            "sale_price_at_release": sale_price,
            "tax_withheld_amount": tax_withheld_value if fmv else None,
            "tax_method": random.choice(
                ["Sell-to-Cover", "Net Issuance", "Cash Payment"]
            ),
            "brokerage_account": f"BR-{random.randint(100000, 999999)}",
            "release_status": random.choice(
                ["Completed", "Completed", "Completed", "Pending", "Failed"]
            ),
            "processed_date": (
                release_dt + timedelta(days=random.randint(0, 3))
            ).strftime("%Y-%m-%d"),
            "processed_by": fake.name(),
            "country": fake.country(),
            "currency": random.choice(["USD", "USD", "USD", "EUR", "GBP", "CAD"]),
            "notes": random.choice(
                [
                    "",
                    "",
                    "",
                    "Manual adjustment required",
                    "Tax rate verified",
                    "Employee requested hold",
                ]
            ),
        }

        release_activities.append(record)

    save_to_json(release_activities, f"release_activities_{release_date}.json")


def save_to_json(data, filename="equity_release_activity.json"):
    """Save the generated data to a JSON file"""
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} records and saved to {filename}")


# Generate sample data
if __name__ == "__main__":
    # Generate data for a specific release date
    release_date = "2024-12-15"
    data = generate_release_activity(num_records=50, release_date=release_date)

    # Save to JSON file
    save_to_json(data, f"release_activity_{release_date}.json")

    # Print sample record
    print("\nSample Record:")
    print(json.dumps(data[0], indent=2))
