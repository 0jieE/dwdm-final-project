from django.db.models import Sum, Count, Max
from datetime import datetime
import pandas as pd

from data_mining.models import Order, OrderItem


class RFMService:

    @staticmethod
    def compute_rfm():
        """
        Computes RFM values per customer
        """

        # Get current date (for recency calculation)
        today = datetime.now().date()

        # Aggregate per customer
        customers = Order.objects.values("customer_id").annotate(
            frequency=Count("id"),
            last_order_date=Max("date__full_date"),
        )

        rfm_data = []

        for c in customers:

            customer_id = c["customer_id"]

            # Recency (days since last purchase)
            recency = (today - c["last_order_date"]).days

            # Monetary (sum of all purchases)
            monetary = OrderItem.objects.filter(
                order__customer_id=customer_id
            ).aggregate(
                total=Sum("total_amount")
            )["total"] or 0

            rfm_data.append({
                "customer_id": customer_id,
                "recency": recency,
                "frequency": c["frequency"],
                "monetary": float(monetary),
            })

        return rfm_data
    
    @staticmethod
    def segment_customers():
        """
        Converts RFM values into customer segments
        """

        data = RFMService.compute_rfm()
        df = pd.DataFrame(data)

        # ------------------------
        # RFM SCORING (1–5)
        # ------------------------

        df["R_score"] = pd.qcut(df["recency"], 5, labels=[5,4,3,2,1])
        df["F_score"] = pd.qcut(df["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
        df["M_score"] = pd.qcut(df["monetary"], 5, labels=[1,2,3,4,5])

        # Convert to int
        df["R_score"] = df["R_score"].astype(int)
        df["F_score"] = df["F_score"].astype(int)
        df["M_score"] = df["M_score"].astype(int)

        # Combined score
        df["RFM_score"] = (
            df["R_score"].astype(str) +
            df["F_score"].astype(str) +
            df["M_score"].astype(str)
        )

        # ------------------------
        # SEGMENT RULES
        # ------------------------

        def segment(row):
            if row["F_score"] >= 4 and row["M_score"] >= 4:
                return "Champions"
            elif row["F_score"] >= 3 and row["M_score"] >= 3:
                return "Loyal Customers"
            elif row["R_score"] <= 2:
                return "At Risk"
            else:
                return "Potential Customers"

        df["segment"] = df.apply(segment, axis=1)

        return df.to_dict(orient="records")