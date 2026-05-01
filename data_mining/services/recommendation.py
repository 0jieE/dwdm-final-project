from .analytics import AnalyticsService
from .rfm import RFMService


class RecommendationEngine:

    # -----------------------------
    # 1. PRODUCT RECOMMENDATIONS (FROM APRIORI)
    # -----------------------------
    @staticmethod
    def product_recommendations():
        rules = AnalyticsService.run_apriori()

        recommendations = []

        top_rules = rules.sort_values(by="lift", ascending=False).head(10)

        for _, row in top_rules.iterrows():
            antecedent = ", ".join(list(row["antecedents"]))
            consequent = ", ".join(list(row["consequents"]))

            recommendations.append({
                "type": "Product Bundle",
                "message": f"Bundle '{antecedent}' with '{consequent}'",
                "reason": f"High lift ({round(row['lift'], 2)}) indicates strong association."
            })

        return recommendations


    # -----------------------------
    # 2. CUSTOMER STRATEGY (FROM RFM)
    # -----------------------------
    @staticmethod
    def customer_recommendations():
        customers = RFMService.segment_customers()

        insights = {
            "Champions": "Offer premium products and early access promotions.",
            "Loyal Customers": "Provide loyalty rewards and cross-sell recommendations.",
            "At Risk": "Send discount campaigns or win-back offers.",
            "Potential Customers": "Encourage first repeat purchase with incentives."
        }

        output = []

        for c in customers:
            segment = c["segment"]

            output.append({
                "customer_id": c["customer_id"],
                "segment": segment,
                "recommendation": insights.get(segment, "No strategy defined")
            })

        return output


    # -----------------------------
    # 3. COMBINED BUSINESS INSIGHTS
    # -----------------------------
    @staticmethod
    def full_recommendations():
        return {
            "product_recommendations": RecommendationEngine.product_recommendations(),
            "customer_recommendations": RecommendationEngine.customer_recommendations()
        }