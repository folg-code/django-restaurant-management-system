from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse

from django.utils import timezone


class Cook(AbstractUser):
    years_of_experience = models.IntegerField(default=0)
    salary = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def get_absolute_url(self):
        return reverse("kitchen:cook-detail", kwargs={"pk": self.pk})

class DishType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    stock_amount = models.FloatField(help_text="Ilość w magazynie (np. kg, litry, szt.)")
    price_per_unit = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    purchase_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.stock_amount})"




class Dish(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    dish_type = models.ForeignKey(DishType, on_delete=models.CASCADE)
    cooks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='dishes')
    ingredients = models.ManyToManyField(Ingredient, through="DishIngredient")

    def __str__(self):
        return self.name


class DishIngredient(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount_required = models.FloatField(help_text="Ilość składnika potrzebna na 1 porcję")

    class Meta:
        unique_together = ("dish", "ingredient")

    def __str__(self):
        return f"{self.amount_required} of {self.ingredient.name} for {self.dish.name}"


class Order(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    dishes = models.ManyToManyField(Dish, through="OrderItem")

    def __str__(self):
        return f"Order #{self.id} ({self.created_at.date()})"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def process_order(self):
        with transaction.atomic():
            for item in self.items.all():
                for di in item.dish.dishingredient_set.all():
                    di.ingredient.stock_amount -= di.amount_required * item.quantity
                    di.ingredient.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.dish.price * self.quantity


