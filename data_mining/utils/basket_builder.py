from collections import defaultdict
from data_mining.models import OrderItem


class BasketBuilder:
    """
    Converts transactional DB data into basket format
    for association rule mining (Apriori).
    """

    @staticmethod
    def build_baskets():
        baskets = defaultdict(list)

        items = OrderItem.objects.select_related('product', 'order')

        for item in items:
            baskets[item.order_id].append(item.product.product_name) # type: ignore

        return dict(baskets)

    @staticmethod
    def build_baskets_list():
        """
        Returns format:
        [
            ['Milk', 'Bread'],
            ['Rice', 'Eggs']
        ]
        """
        baskets = BasketBuilder.build_baskets()
        return list(baskets.values())