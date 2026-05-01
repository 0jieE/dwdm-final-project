from django.core.management.base import BaseCommand
import pandas as pd

from data_mining.models import (
    Month, Date,
    Department, Category, Brand, Product,
    Location, Customer, Store,
    Order, OrderItem
)


class Command(BaseCommand):
    help = "Load Data Warehouse from Excel with ETL (Cleaning + Transformation)"

    def handle(self, *args, **kwargs):
        file_path = "final_realistic_dataset.xlsx"

        self.stdout.write(self.style.SUCCESS("🚀 Starting ETL Process..."))

        # ----------------------
        # EXTRACT
        # ----------------------
        sheets = pd.read_excel(file_path, sheet_name=None)

        df_month = sheets["Month"]
        df_date = sheets["Date"]
        df_department = sheets["Department"]
        df_category = sheets["Category"]
        df_brand = sheets["Brand"]
        df_product = sheets["Product"]
        df_location = sheets["Location"]
        df_customer = sheets["Customer"]
        df_store = sheets["Store"]
        df_order = sheets["Order"]
        df_orderitem = sheets["OrderItem"]

        # ----------------------
        # TRANSFORM (CLEANING)
        # ----------------------

        def clean_df(df, name):
            original = len(df)

            # remove duplicates
            df = df.drop_duplicates()

            # drop rows with nulls
            df = df.dropna()

            self.stdout.write(f"🧹 {name}: {original} → {len(df)} rows after cleaning")

            return df

        df_month = clean_df(df_month, "Month")
        df_date = clean_df(df_date, "Date")
        df_department = clean_df(df_department, "Department")
        df_category = clean_df(df_category, "Category")
        df_brand = clean_df(df_brand, "Brand")
        df_product = clean_df(df_product, "Product")
        df_location = clean_df(df_location, "Location")
        df_customer = clean_df(df_customer, "Customer")
        df_store = clean_df(df_store, "Store")
        df_order = clean_df(df_order, "Order")
        df_orderitem = clean_df(df_orderitem, "OrderItem")

        # ----------------------
        # LOAD
        # ----------------------

        # clear old data
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Brand.objects.all().delete()
        Category.objects.all().delete()
        Department.objects.all().delete()
        Customer.objects.all().delete()
        Store.objects.all().delete()
        Location.objects.all().delete()
        Date.objects.all().delete()
        Month.objects.all().delete()

        self.stdout.write("🗑 Old data cleared")

        # ----------------------
        # INSERT DIMENSIONS
        # ----------------------

        # Month
        month_map = {}
        for _, row in df_month.iterrows():
            obj = Month.objects.create(
                id=row["month_id"],
                month_name=row["month_name"],
                quarter=row["quarter"]
            )
            month_map[row["month_id"]] = obj

        # Date
        date_map = {}
        for _, row in df_date.iterrows():
            obj = Date.objects.create(
                id=row["date_id"],
                full_date=row["full_date"],
                day=row["day"],
                month=month_map[row["month_id"]],
                year=row["year"]
            )
            date_map[row["date_id"]] = obj

        # Department
        dept_map = {}
        for _, row in df_department.iterrows():
            obj = Department.objects.create(
                id=row["department_id"],
                department_name=row["department_name"]
            )
            dept_map[row["department_id"]] = obj

        # Category
        cat_map = {}
        for _, row in df_category.iterrows():
            obj = Category.objects.create(
                id=row["category_id"],
                category_name=row["category_name"],
                department=dept_map[row["department_id"]]
            )
            cat_map[row["category_id"]] = obj

        # Brand
        brand_map = {}
        for _, row in df_brand.iterrows():
            obj = Brand.objects.create(
                id=row["brand_id"],
                brand_name=row["brand_name"]
            )
            brand_map[row["brand_id"]] = obj

        # Product
        product_map = {}
        for _, row in df_product.iterrows():
            obj = Product.objects.create(
                id=row["product_id"],
                product_name=row["product_name"],
                category=cat_map[row["category_id"]],
                brand=brand_map[row["brand_id"]],
                price=row["price"]
            )
            product_map[row["product_id"]] = obj

        # Location
        loc_map = {}
        for _, row in df_location.iterrows():
            obj = Location.objects.create(
                id=row["location_id"],
                barangay=row["barangay"],
                city=row["city"],
                region=row["region"]
            )
            loc_map[row["location_id"]] = obj

        # Customer
        cust_map = {}
        for _, row in df_customer.iterrows():
            obj = Customer.objects.create(
                id=row["customer_id"],
                gender=row["gender"],
                age_group=row["age_group"],
                location=loc_map[row["location_id"]]
            )
            cust_map[row["customer_id"]] = obj

        # Store
        store_map = {}
        for _, row in df_store.iterrows():
            obj = Store.objects.create(
                id=row["store_id"],
                store_name=row["store_name"],
                location=loc_map[row["location_id"]]
            )
            store_map[row["store_id"]] = obj

        # ----------------------
        # FACT TABLE
        # ----------------------

        order_map = {}
        for _, row in df_order.iterrows():
            obj = Order.objects.create(
                id=row["order_id"],
                date=date_map[row["date_id"]],
                customer=cust_map[row["customer_id"]],
                store=store_map[row["store_id"]]
            )
            order_map[row["order_id"]] = obj

        for _, row in df_orderitem.iterrows():
            OrderItem.objects.create(
                id=row["order_item_id"],
                order=order_map[row["order_id"]],
                product=product_map[row["product_id"]],
                quantity=row["quantity"],
                total_amount=row["total_amount"]
            )

        self.stdout.write(self.style.SUCCESS("✅ ETL Completed Successfully!"))

