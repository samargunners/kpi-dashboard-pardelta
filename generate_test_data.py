"""
Test Data Generator for Pardelta Dashboard

This script generates sample data for testing the dashboard without a live Supabase connection.
Useful for development and demonstration purposes.
"""

import pandas as pd
import random
from datetime import datetime, timedelta

# Store configuration
STORES = [
    {"pc_number": "301290", "store_name": "Paxton", "store_id": 301290},
    {"pc_number": "343939", "store_name": "Mt Joy", "store_id": 343939},
    {"pc_number": "357993", "store_name": "Enola", "store_id": 357993},
    {"pc_number": "358529", "store_name": "Columbia", "store_id": 358529},
    {"pc_number": "359042", "store_name": "Lititz", "store_id": 359042},
    {"pc_number": "362913", "store_name": "Eisenhower", "store_id": 362913},
    {"pc_number": "363271", "store_name": "Marietta", "store_id": 363271},
    {"pc_number": "364322", "store_name": "ETown", "store_id": 364322},
]

LABOR_POSITIONS = [
    "DD Crew Plus",
    "DD Crew Standard",
    "DD Shift Leader Plus",
    "DD Manager",
    "DD Manager - Salary",
]


def generate_hme_data(days: int = 30) -> pd.DataFrame:
    """Generate sample HME report data."""
    records = []
    end_date = datetime.now().date()
    
    for i in range(days):
        date = end_date - timedelta(days=i)
        
        for store in STORES:
            for daypart in range(1, 6):
                # Generate realistic lane_total times
                base_time = 145 + random.randint(-15, 30)
                
                # Daypart 2 is typically faster
                if daypart == 2:
                    base_time = max(130, base_time - 10)
                
                records.append({
                    "date": date,
                    "store": store["store_id"],
                    "time_measure": f"Daypart {daypart}",
                    "lane_total": base_time + random.randint(-5, 15),
                    "menu_all": random.randint(25, 50),
                    "greet_all": random.randint(2, 10),
                    "service": random.randint(70, 120),
                    "lane_queue": random.randint(10, 35),
                    "total_cars": random.randint(8, 25),
                })
    
    return pd.DataFrame(records)


def generate_labor_data(days: int = 30) -> pd.DataFrame:
    """Generate sample labor metrics data."""
    records = []
    end_date = datetime.now().date()
    
    for i in range(days):
        date = end_date - timedelta(days=i)
        
        for store in STORES:
            for position in LABOR_POSITIONS:
                # Skip some positions randomly
                if random.random() < 0.2:
                    continue
                
                # Generate hours and pay
                reg_hours = random.uniform(20, 50)
                ot_hours = random.uniform(0, 10)
                hourly_rate = 12 + random.uniform(0, 8)
                
                reg_pay = reg_hours * hourly_rate
                ot_pay = ot_hours * hourly_rate * 1.5
                
                # Percent labor varies by store
                base_percent = 0.18 + random.uniform(0, 0.08)
                
                records.append({
                    "date": date,
                    "store": store["store_name"],
                    "pc_number": store["pc_number"],
                    "labor_position": position,
                    "reg_hours": reg_hours,
                    "ot_hours": ot_hours,
                    "total_hours": reg_hours + ot_hours,
                    "reg_pay": reg_pay,
                    "ot_pay": ot_pay,
                    "total_pay": reg_pay + ot_pay,
                    "percent_labor": base_percent * random.uniform(0.8, 1.2),
                })
    
    return pd.DataFrame(records)


def generate_medallia_data(days: int = 30, responses_per_day: int = 5) -> pd.DataFrame:
    """Generate sample Medallia/OSAT data."""
    records = []
    end_date = datetime.now().date()
    
    for i in range(days):
        date = end_date - timedelta(days=i)
        
        for store in STORES:
            # Generate random number of responses per day
            num_responses = random.randint(1, responses_per_day * 2)
            
            for _ in range(num_responses):
                # Most scores are 4-5, some are lower
                if random.random() < 0.7:
                    osat = random.choice([4, 5])
                    ltr = random.randint(8, 10)
                else:
                    osat = random.randint(1, 4)
                    ltr = random.randint(0, 8)
                
                records.append({
                    "report_date": date,
                    "pc_number": store["pc_number"],
                    "restaurant_address": f"{store['store_name']} Location",
                    "order_channel": random.choice(["In-store", "Drive-thru", "Mobile"]),
                    "transaction_datetime": datetime.combine(date, datetime.min.time()) + timedelta(hours=random.randint(6, 20)),
                    "response_datetime": datetime.combine(date, datetime.min.time()) + timedelta(hours=random.randint(6, 22)),
                    "osat": osat,
                    "ltr": ltr,
                    "accuracy": random.choice(["Yes", "No"]),
                    "comment": "Sample comment" if random.random() < 0.5 else None,
                })
    
    return pd.DataFrame(records)


def main():
    """Generate and save test data."""
    print("🔧 Generating test data...")
    
    # Generate data
    hme_df = generate_hme_data(days=30)
    labor_df = generate_labor_data(days=30)
    medallia_df = generate_medallia_data(days=30)
    
    # Save to CSV
    hme_df.to_csv("test_data_hme.csv", index=False)
    labor_df.to_csv("test_data_labor.csv", index=False)
    medallia_df.to_csv("test_data_medallia.csv", index=False)
    
    print(f"✅ Generated {len(hme_df)} HME records")
    print(f"✅ Generated {len(labor_df)} Labor records")
    print(f"✅ Generated {len(medallia_df)} Medallia records")
    print("\nFiles saved:")
    print("  - test_data_hme.csv")
    print("  - test_data_labor.csv")
    print("  - test_data_medallia.csv")
    print("\nYou can import these into Supabase for testing.")


if __name__ == "__main__":
    main()