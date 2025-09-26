from decimal import Decimal

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Prefetch
from django.urls import reverse

from django.utils import timezone


class Cook(AbstractUser):
    years_of_experience = models.IntegerField(default=0)
    salary = models.DecimalField(max_digits=8, decimal_places=2, default=0, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("kitchen:cook-detail", kwargs={"pk": self.pk})



class DishType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20, default="kg", help_text="Unit e.g., kg, l, pcs")
    stock_amount = models.FloatField(default=0, help_text="Current stock")

    @property
    def price_per_unit(self):

        purchases = self.transactions.filter(transaction_type=IngredientTransaction.SUPPLY)
        total_qty = sum(t.quantity for t in purchases)
        if total_qty == 0:
            return Decimal("0.00")
        total_cost = sum(Decimal(t.quantity) * Decimal(t.price_per_unit) for t in purchases)
        return total_cost / Decimal(total_qty)

    def __str__(self):
        return f"{self.name} ({self.stock_amount} {self.unit} {self.price_per_unit})"


class IngredientTransaction(models.Model):
    SUPPLY = "SUPPLY"
    WASTE = "WASTE"

    TRANSACTION_CHOICES = [
        (SUPPLY, "Supply"),
        (WASTE, "Waste"),

    ]
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_CHOICES
    )
    quantity = models.FloatField()
    price_per_unit = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateField(blank=True, null=True, help_text="Required for SUPPLY")
    note = models.TextField(blank=True, null=True)

    source_transactions = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='waste_used_in',
        limit_choices_to={'transaction_type': SUPPLY}
    )

    def apply_waste(self):

        if self.transaction_type != self.WASTE:
            return

        if self.quantity > self.ingredient.stock_amount:
            raise ValueError("Cannot waste more than available stock")


        self.ingredient.stock_amount -= self.quantity
        self.ingredient.save(update_fields=['stock_amount'])


    def save(self, *args, **kwargs):
        if self.transaction_type == self.SUPPLY:
            if not self.expiration_date:
                raise ValueError("Expiration date is required for supply transactions")
            self.ingredient.stock_amount += self.quantity
            self.ingredient.save(update_fields=['stock_amount'])


        super().save(*args, **kwargs)
        if self.transaction_type == self.WASTE:
            self.apply_waste()

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.ingredient.unit} of {self.ingredient.name}"



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
        unique_together = ("dish", "amount_required")

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


class FinanceManager:
    def __init__(self):
        today = timezone.now().date()

        self.ingredients = Ingredient.objects.prefetch_related(
            Prefetch(
                'transactions',
                queryset=IngredientTransaction.objects.filter(transaction_type=IngredientTransaction.SUPPLY),
                to_attr='supply_transactions'
            )
        )

        self.orders = Order.objects.prefetch_related(
            'items__dish__dishingredient_set__ingredient'
        )

        self.cooks = Cook.objects.all()

    @property
    def supply_on_stock(self):

        total = Decimal("0.00")
        for ingredient in self.ingredients:
            qty = Decimal(str(ingredient.stock_amount))
            price = ingredient.price_per_unit
            total += qty * price
        return total

    @property
    def supply_cost(self):

        total = Decimal("0.00")
        for ingredient in self.ingredients:
            for t in ingredient.transactions.filter(transaction_type=IngredientTransaction.SUPPLY):
                total += Decimal(str(t.quantity)) * Decimal(str(t.price_per_unit))
        return total

    @property
    def revenue(self):
        return sum(Decimal(order.total_price) for order in self.orders)

    @property
    def employee_costs(self):
        return sum(Decimal(cook.salary) for cook in self.cooks)

    @property
    def fixed_costs(self):
        return Decimal("1000.00")

    @property
    def net_profit(self):

        return self.revenue - (self.employee_costs + self.fixed_costs + self.supply_cost)

    @property
    def profit_with_stock(self):

        return self.net_profit + self.supply_on_stock
