from django.db import models

class Dish(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)  # Add 'available' field
    quantity = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.quantity <= 0:
            self.available = False
        super().save(*args, **kwargs)

class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    dishes = models.ManyToManyField(Dish, blank=True)  # Add blank=True to allow empty orders
    status = models.CharField(max_length=50)
class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
