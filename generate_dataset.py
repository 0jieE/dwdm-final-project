import random
import pandas as pd
from faker import Faker # type: ignore
from datetime import datetime, timedelta

fake = Faker()

# ----------------------
# CONFIG
# ----------------------
NUM_CUSTOMERS = 100
NUM_STORES = 10
NUM_ORDERS = 300

# ----------------------
# DOMAIN DATA (STRICT MAPPING)
# ----------------------
DATA = {
    "Grocery": {
        "Milk": ["Nestle", "Alaska"],
        "Bread": ["Gardenia"],
        "Coffee": ["Nescafe"],
        "Chips": ["Oishi", "Piattos"],
        "Soda": ["Coca-Cola", "Pepsi"],
        "Rice": ["Dinorado"]
    },
    "Electronics": {
        "Smartphone": ["Samsung", "Xiaomi", "Apple", "Realme"],
        "Laptop": ["Dell", "HP", "Apple"],
        "Headphones": ["JBL", "Sony"],
        "Charger": ["Anker", "Bavin"],
        "Powerbank": ["Romoss", "Anker"]
    },
    "Clothing": {
        "T-Shirt": ["Bench", "Penshoppe"],
        "Jeans": ["Levis"],
        "Jacket": ["Uniqlo"],
        "Shorts": ["H&M"],
        "Dress": ["Zara"]
    }
}

PRICE_RANGE = {
    "Grocery": (20, 300),
    "Electronics": (500, 5000),
    "Clothing": (200, 1500)
}

BASKETS = [
    ["Chips", "Soda"],
    ["Bread", "Milk"],
    ["Coffee", "Sugar"]
]

# ----------------------
# MONTH
# ----------------------
months = []
for i in range(1, 13):
    months.append({
        "month_id": i,
        "month_name": datetime(2026, i, 1).strftime("%B"),
        "quarter": (i - 1) // 3 + 1
    })

# ----------------------
# DATE
# ----------------------
dates = []
start_date = datetime(2025, 1, 1)
for i in range(365):
    d = start_date + timedelta(days=i)
    dates.append({
        "date_id": i + 1,
        "full_date": d.date(),
        "day": d.day,
        "month_id": d.month,
        "year": d.year,
        "is_weekend": d.weekday() >= 5
    })

# ----------------------
# DEPARTMENT / CATEGORY
# ----------------------
departments = []
categories = []
dept_id = 1
cat_id = 1

for dept_name, items in DATA.items():
    departments.append({
        "department_id": dept_id,
        "department_name": dept_name
    })

    for category_name in items.keys():
        categories.append({
            "category_id": cat_id,
            "category_name": category_name,
            "department_id": dept_id
        })
        cat_id += 1

    dept_id += 1

# ----------------------
# BRAND TABLE
# ----------------------
brands = []
brand_map = {}
brand_id = 1

for dept in DATA:
    for category in DATA[dept]:
        for brand in DATA[dept][category]:
            if brand not in brand_map:
                brand_map[brand] = brand_id
                brands.append({
                    "brand_id": brand_id,
                    "brand_name": brand
                })
                brand_id += 1

# ----------------------
# PRODUCT TABLE (STRICT)
# ----------------------
products = []
product_id = 1

for dept_name, categories_map in DATA.items():
    for category_name, brand_list in categories_map.items():

        category_id = next(
            c["category_id"] for c in categories
            if c["category_name"] == category_name
        )

        for brand in brand_list:
            price = round(random.uniform(*PRICE_RANGE[dept_name]), 2)

            products.append({
                "product_id": product_id,
                "product_name": f"{brand} {category_name}",
                "category_id": category_id,
                "brand_id": brand_map[brand],
                "price": price,
                "weight": random.uniform(0.2, 1.0)
            })

            product_id += 1

# ----------------------
# LOCATION
# ----------------------
locations = []
for i in range(20):
    locations.append({
        "location_id": i + 1,
        "barangay": fake.street_name(),
        "city": "Quezon City",
        "region": "NCR"
    })

# ----------------------
# CUSTOMER
# ----------------------
customers = []
for i in range(NUM_CUSTOMERS):
    customers.append({
        "customer_id": i + 1,
        "gender": random.choice(["M", "F"]),
        "age_group": random.choice(["18-25", "26-35", "36-45", "46-60"]),
        "location_id": random.choice(locations)["location_id"],
        "budget": random.choice(["low", "mid", "high"]),
        "fav_category": random.choice(categories)["category_id"]
    })

# ----------------------
# STORE
# ----------------------
stores = []
for i in range(NUM_STORES):
    stores.append({
        "store_id": i + 1,
        "store_name": fake.company(),
        "location_id": random.choice(locations)["location_id"]
    })

# ----------------------
# HELPERS
# ----------------------
def weighted_choice(items, k):
    weights = [i["weight"] for i in items]
    return random.choices(items, weights=weights, k=k)

def filter_budget(customer, items):
    if customer["budget"] == "low":
        return [p for p in items if p["price"] < 300]
    elif customer["budget"] == "mid":
        return [p for p in items if p["price"] < 1500]
    return items

# ----------------------
# FACT TABLES
# ----------------------
orders = []
order_items = []

order_id = 1
item_id = 1

for _ in range(NUM_ORDERS):
    customer = random.choice(customers)
    date = random.choice(dates)

    orders.append({
        "order_id": order_id,
        "date_id": date["date_id"],
        "customer_id": customer["customer_id"],
        "store_id": random.choice(stores)["store_id"]
    })

    available = filter_budget(customer, products)

    preferred = [p for p in available if p["category_id"] == customer["fav_category"]]
    if preferred and random.random() < 0.7:
        available = preferred

    num_items = max(1, int(random.gauss(3, 1)))
    selected = weighted_choice(available, num_items)

    # basket injection (only valid categories)
    if random.random() < 0.3:
        basket = random.choice(BASKETS)
        for keyword in basket:
            for p in products:
                if keyword.lower() in p["product_name"].lower():
                    selected.append(p)
                    break

    for p in selected:
        qty = random.randint(1, 3)
        total = round(qty * p["price"], 2)

        order_items.append({
            "order_item_id": item_id,
            "order_id": order_id,
            "product_id": p["product_id"],
            "quantity": qty,
            "total_amount": total
        })

        item_id += 1

    order_id += 1

# ----------------------
# EXPORT
# ----------------------
with pd.ExcelWriter("final_realistic_dataset.xlsx", engine="openpyxl") as writer:
    pd.DataFrame(months).to_excel(writer, sheet_name="Month", index=False)
    pd.DataFrame(dates).to_excel(writer, sheet_name="Date", index=False)
    pd.DataFrame(departments).to_excel(writer, sheet_name="Department", index=False)
    pd.DataFrame(categories).to_excel(writer, sheet_name="Category", index=False)
    pd.DataFrame(brands).to_excel(writer, sheet_name="Brand", index=False)
    pd.DataFrame(products).drop(columns=["weight"]).to_excel(writer, sheet_name="Product", index=False)
    pd.DataFrame(locations).to_excel(writer, sheet_name="Location", index=False)
    pd.DataFrame(customers).drop(columns=["budget", "fav_category"]).to_excel(writer, sheet_name="Customer", index=False)
    pd.DataFrame(stores).to_excel(writer, sheet_name="Store", index=False)
    pd.DataFrame(orders).to_excel(writer, sheet_name="Order", index=False)
    pd.DataFrame(order_items).to_excel(writer, sheet_name="OrderItem", index=False)

print("✅ FINAL realistic dataset generated: final_realistic_dataset.xlsx")