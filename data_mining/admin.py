from django.contrib import admin
from .models import (
    Month, Date,
    Department, Category, Brand, Product,
    Location, Customer,
    Store,
    Order, OrderItem
)


# ----------------------
# DATE
# ----------------------

@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    list_display = ('id', 'month_name', 'quarter')
    search_fields = ('month_name',)


@admin.register(Date)
class DateAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_date', 'day', 'month', 'year')
    list_filter = ('year', 'month')
    search_fields = ('full_date',)


# ----------------------
# PRODUCT
# ----------------------

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'department_name')
    search_fields = ('department_name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'department')
    list_filter = ('department',)
    search_fields = ('category_name',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand_name')
    search_fields = ('brand_name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'category', 'brand', 'price')
    list_filter = ('category', 'brand')
    search_fields = ('product_name',)


# ----------------------
# LOCATION & CUSTOMER
# ----------------------

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'barangay', 'city', 'region')
    list_filter = ('city', 'region')
    search_fields = ('barangay', 'city')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'gender', 'age_group', 'location')
    list_filter = ('gender', 'age_group')
    search_fields = ('id',)


# ----------------------
# STORE
# ----------------------

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'store_name', 'location')
    list_filter = ('location',)
    search_fields = ('store_name',)


# ----------------------
# ORDER + ORDER ITEMS
# ----------------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'customer', 'store')
    list_filter = ('date', 'store')
    search_fields = ('id',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'total_amount')
    list_filter = ('product',)
    search_fields = ('order__id',)