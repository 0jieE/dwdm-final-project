from django.urls import path
from . import views

urlpatterns = [
    # -------------------------
    # MARKET BASKET DASHBOARD
    # -------------------------
    path("dashboard/basket/", views.basket_dashboard, name="basket_dashboard"),

    path("api/apriori/rules/", views.apriori_rules),
    path("api/apriori/insights/", views.apriori_insights),
    path("api/apriori/baskets/", views.baskets_view),

    # -------------------------
    # CUSTOMER SEGMENTATION DASHBOARD
    # -------------------------
    path("dashboard/rfm/", views.rfm_dashboard, name="rfm_dashboard"),

    path("api/rfm/segments/", views.rfm_segments),

    # recommendation engine 
    path("dashboard/recommendations/", views.recommendation_dashboard, name="recommendation_dashboard"),
    path("api/recommendations/", views.recommendations_view),

    # dataset view for validation
    path("api/dataset/", views.dataset_view, name="dataset_view"),
    path("", views.dataset_page, name="dataset_page"),

]