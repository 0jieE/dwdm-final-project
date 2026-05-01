from collections import defaultdict
import pandas as pd

from mlxtend.preprocessing import TransactionEncoder # type: ignore
from mlxtend.frequent_patterns import apriori, association_rules # type: ignore

from data_mining.models import OrderItem


class AnalyticsService:
    """
    Core analytics service for:
    - Basket conversion
    - Apriori association rule mining
    - Insight extraction
    """

    # -----------------------------
    # 1. BASKET GENERATION
    # -----------------------------
    @staticmethod
    def get_baskets():
        """
        Convert transactional data into baskets:
        {order_id: [product1, product2, ...]}
        """
        baskets = defaultdict(list)

        items = OrderItem.objects.select_related('product', 'order')

        for item in items:
            baskets[item.order_id].append(item.product.product_name) # type: ignore

        return dict(baskets)

    # -----------------------------
    # 2. CONVERT TO APRIORI FORMAT
    # -----------------------------
    @staticmethod
    def get_basket_dataframe():
        """
        Convert baskets into one-hot encoded DataFrame
        required for Apriori algorithm
        """
        baskets = AnalyticsService.get_baskets()
        transactions = list(baskets.values())

        te = TransactionEncoder()
        te_array = te.fit(transactions).transform(transactions)

        df = pd.DataFrame(te_array, columns=te.columns_)

        return df

    # -----------------------------
    # 3. RUN APRIORI ALGORITHM
    # -----------------------------
    @staticmethod
    def run_apriori(min_support=0.02, min_confidence=0.3):
        """
        Generate association rules from transactions
        """
        df = AnalyticsService.get_basket_dataframe()

        # frequent itemsets
        frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)

        # association rules
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=min_confidence
        )

        # sort by lift (most meaningful relationships first)
        rules = rules.sort_values(by="lift", ascending=False)

        return rules

    # -----------------------------
    # 4. TOP INSIGHTS (FOR DASHBOARD)
    # -----------------------------
    @staticmethod
    def get_top_rules(limit=10):
        """
        Returns most important association rules
        """
        rules = AnalyticsService.run_apriori()

        top_rules = rules.head(limit)[
            ["antecedents", "consequents", "support", "confidence", "lift"]
        ]

        return top_rules

    # -----------------------------
    # 5. SUMMARY INSIGHTS (FOR REPORT)
    # -----------------------------
    @staticmethod
    def get_insight_summary():
        """
        Converts rules into human-readable insights
        (useful for thesis documentation)
        """
        rules = AnalyticsService.get_top_rules()

        insights = []

        for _, row in rules.iterrows():
            antecedents = ", ".join(list(row["antecedents"]))
            consequents = ", ".join(list(row["consequents"]))

            insights.append({
                "rule": f"{antecedents} → {consequents}",
                "support": round(row["support"], 3),
                "confidence": round(row["confidence"], 3),
                "lift": round(row["lift"], 3),
                "interpretation": f"Customers who buy {antecedents} are likely to also buy {consequents}."
            })

        return insights