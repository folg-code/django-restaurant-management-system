from django.test import TestCase
from django.utils import timezone
from decimal import Decimal

from kitchen.models import (
    Chef, DishType, Dish, Ingredient,
    IngredientTransaction, Order, OrderItem, FinanceManager
)

class FinanceManagerTests(TestCase):
    def setUp(self):

        self.chef = Chef.objects.create_user(
            username="chef1",
            password="pass123",
            salary=500
        )

        self.ing1 = Ingredient.objects.create(name="Tomato", unit="kg", stock_amount=0)
        self.ing2 = Ingredient.objects.create(name="Cheese", unit="kg", stock_amount=0)


        IngredientTransaction.objects.create(
            ingredient=self.ing1,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=10,
            price_per_unit=2,
            expiration_date=timezone.now().date(),
        )
        IngredientTransaction.objects.create(
            ingredient=self.ing2,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=5,
            price_per_unit=4,
            expiration_date=timezone.now().date(),
        )

        dish_type = DishType.objects.create(name="Main")
        self.dish = Dish.objects.create(
            name="Pizza",
            description="Test dish",
            price=Decimal("20.00"),
            dish_type=dish_type
        )

        self.order = Order.objects.create()
        OrderItem.objects.create(order=self.order, dish=self.dish, quantity=2)

        self.fm = FinanceManager()

    def test_supply_on_stock(self):
        expected = Decimal("10") * Decimal("2") + Decimal("5") * Decimal("4")
        self.assertEqual(self.fm.supply_on_stock, expected)

    def test_supply_cost(self):
        expected = Decimal("10") * Decimal("2") + Decimal("5") * Decimal("4")
        self.assertEqual(self.fm.supply_cost, expected)

    def test_revenue(self):
        self.assertEqual(self.fm.revenue, Decimal("40.00"))

    def test_employee_costs(self):
        self.assertEqual(self.fm.employee_costs, Decimal("500"))

    def test_fixed_costs(self):
        self.assertEqual(self.fm.fixed_costs, Decimal("1000.00"))

    def test_net_profit(self):
        revenue = Decimal("40.00")
        costs = self.fm.supply_cost + self.fm.employee_costs + self.fm.fixed_costs
        expected = revenue - costs
        self.assertEqual(self.fm.net_profit, expected)

    def test_profit_with_stock(self):
        expected = self.fm.net_profit + self.fm.supply_on_stock
        self.assertEqual(self.fm.profit_with_stock, expected)