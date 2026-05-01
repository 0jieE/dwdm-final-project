from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from data_mining.models import OrderItem

from .services.rfm import RFMService
from .services.analytics import AnalyticsService
from .services.recommendation import RecommendationEngine


@require_GET
def apriori_rules(request):
    """
    Returns raw association rules (for debugging / API / frontend charts)
    """
    rules = AnalyticsService.run_apriori()

    data = rules[[
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift"
    ]].head(20)

    # convert frozenset → list (JSON safe)
    response = []
    for _, row in data.iterrows():
        response.append({
            "antecedents": list(row["antecedents"]),
            "consequents": list(row["consequents"]),
            "support": float(row["support"]),
            "confidence": float(row["confidence"]),
            "lift": float(row["lift"]),
        })

    return JsonResponse({"rules": response})


@require_GET
def apriori_insights(request):
    """
    Returns human-readable insights for thesis/dashboard
    """
    insights = AnalyticsService.get_insight_summary()

    return JsonResponse({
        "count": len(insights),
        "insights": insights
    })


@require_GET
def baskets_view(request):
    """
    Returns transaction baskets for validation
    """
    baskets = AnalyticsService.get_baskets()

    sample = dict(list(baskets.items())[:10])

    return JsonResponse({
        "total_transactions": len(baskets),
        "sample": sample
    })


@require_GET
def rfm_segments(request):
    """
    Returns customer segmentation based on RFM
    """
    data = RFMService.segment_customers()

    return JsonResponse({
        "count": len(data),
        "segments": data
    })


@require_GET
def recommendations_view(request):
    """
    Business recommendation engine output
    """
    data = RecommendationEngine.full_recommendations()

    return JsonResponse(data)

def dataset_view(request):
    """
    Informative dataset explorer based on warehouse models
    Shows relational + hierarchical data
    """

    items = OrderItem.objects.select_related(
        'order',
        'order__date',
        'order__customer',
        'order__store',
        'product',
        'product__category',
        'product__category__department',
        'product__brand',
        'order__customer__location',
        'order__store__location',
    )[:100]

    data = []

    for item in items:
        data.append({
            # ---------------- Order Level ----------------
            "order_id": item.order.id, # type: ignore
            "date": item.order.date.full_date,
            "day": item.order.date.day,
            "month": item.order.date.month.month_name,
            "year": item.order.date.year,

            # ---------------- Customer ----------------
            "customer_id": item.order.customer.id, # type: ignore
            "gender": item.order.customer.gender,
            "age_group": item.order.customer.age_group,
            "customer_location": f"{item.order.customer.location.barangay}, {item.order.customer.location.city}",

            # ---------------- Store ----------------
            "store": item.order.store.store_name,
            "store_location": f"{item.order.store.location.city}, {item.order.store.location.region}",

            # ---------------- Product Hierarchy ----------------
            "product": item.product.product_name,
            "category": item.product.category.category_name,
            "department": item.product.category.department.department_name,
            "brand": item.product.brand.brand_name,
            "price": float(item.product.price),

            # ---------------- Fact Measures ----------------
            "quantity": item.quantity,
            "total_amount": float(item.total_amount),
        })

    return JsonResponse({
        "count": len(data),
        "dataset": data
    })


def dataset_page(request):
    return render(request, "analytics/dataset.html")

def recommendation_dashboard(request):
    """
    Dashboard to display recommendations
    """
    return render(request, "analytics/recommendation_dashboard.html")


def basket_dashboard(request):
    """
    Market Basket Analysis Dashboard
    """
    return render(request, "analytics/basket_dashboard.html")


def rfm_dashboard(request):
    """
    Customer Segmentation Dashboard
    """
    return render(request, "analytics/rfm_dashboard.html")
