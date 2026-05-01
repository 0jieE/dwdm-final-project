from django.db import models


# ----------------------
# DATE DIMENSIONS
# ----------------------

class Month(models.Model):
    month_name = models.CharField(max_length=20)
    quarter = models.IntegerField()

    def __str__(self):
        return self.month_name


class Date(models.Model):
    full_date = models.DateField()
    day = models.IntegerField()
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    year = models.IntegerField()

    def __str__(self):
        return str(self.full_date)


# ----------------------
# PRODUCT DIMENSIONS
# ----------------------

class Department(models.Model):
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    brand_name = models.CharField(max_length=100)

    def __str__(self):
        return self.brand_name


class Product(models.Model):
    product_name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product_name


# ----------------------
# LOCATION & CUSTOMER
# ----------------------

class Location(models.Model):
    barangay = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.barangay}, {self.city}"


class Customer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age_group = models.CharField(max_length=50)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"Customer {self.id}" # type: ignore


# ----------------------
# STORE
# ----------------------

class Store(models.Model):
    store_name = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.store_name


# ----------------------
# FACT TABLE (ORDER)
# ----------------------

class Order(models.Model):
    date = models.ForeignKey(Date, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id}" # type: ignore


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Order {self.order.id} - {self.product.product_name}" # type: ignore