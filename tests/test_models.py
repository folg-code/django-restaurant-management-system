from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError

from kitchen.models import (
    Chef, DishType, Ingredient, IngredientTransaction,
    Dish, DishIngredient, Order, OrderItem, FinanceManager
)


class ChefModelTest(TestCase):
    def test_get_absolute_url(self):
        chef = Chef.objects.create_user(username="chef1", password="pass")
        self.assertIn(f"/chefs/{chef.pk}/", chef.get_absolute_url())


class DishTypeModelTest(TestCase):
    def test_str(self):
        dt = DishType.objects.create(name="Pizza")
        self.assertEqual(str(dt), "Pizza")


class IngredientModelTest(TestCase):
    def test_price_per_unit_no_supply(self):
        ing = Ingredient.objects.create(name="Tomato", unit="kg")
        self.assertEqual(ing.price_per_unit, Decimal("0.00"))

    def test_price_per_unit_with_supplies(self):
        ing = Ingredient.objects.create(name="Tomato", unit="kg")
        IngredientTransaction.objects.create(
            ingredient=ing,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=10,
            price_per_unit=2,
            expiration_date=timezone.now().date(),
        )
        IngredientTransaction.objects.create(
            ingredient=ing,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=20,
            price_per_unit=4,
            expiration_date=timezone.now().date(),
        )
        self.assertEqual(round(ing.price_per_unit, 2), Decimal("3.33"))

    def test_str_representation(self):
        ing = Ingredient.objects.create(name="Cheese", unit="kg", stock_amount=5)
        self.assertIn("Cheese", str(ing))


class IngredientTransactionModelTest(TestCase):
    def test_supply_increases_stock(self):
        ing = Ingredient.objects.create(name="Flour", unit="kg", stock_amount=0)
        IngredientTransaction.objects.create(
            ingredient=ing,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=5,
            price_per_unit=2,
            expiration_date=timezone.now().date(),
        )
        ing.refresh_from_db()
        self.assertEqual(ing.stock_amount, 5)

    def test_supply_requires_expiration_date(self):
        ing = Ingredient.objects.create(name="Butter", unit="kg")
        with self.assertRaises(ValueError):
            IngredientTransaction.objects.create(
                ingredient=ing,
                transaction_type=IngredientTransaction.SUPPLY,
                quantity=5,
                price_per_unit=1,
            )

    def test_waste_reduces_stock(self):
        ing = Ingredient.objects.create(name="Eggs", unit="pcs", stock_amount=0)
        IngredientTransaction.objects.create(
            ingredient=ing,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=10,
            price_per_unit=1,
            expiration_date=timezone.now().date(),
        )
        IngredientTransaction.objects.create(
            ingredient=ing,
            transaction_type=IngredientTransaction.WASTE,
            quantity=4,
            price_per_unit=0,
        )
        ing.refresh_from_db()
        self.assertEqual(ing.stock_amount, 6)

    def test_waste_more_than_stock_raises(self):
        ing = Ingredient.objects.create(name="Milk", unit="l", stock_amount=3)
        with self.assertRaises(ValueError):
            IngredientTransaction.objects.create(
                ingredient=ing,
                transaction_type=IngredientTransaction.WASTE,
                quantity=5,
                price_per_unit=0,
            )

    def test_str(self):
        ing = Ingredient.objects.create(name="Oil", unit="l")
        tx = IngredientTransaction.objects.create(
            ingredient=ing,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=2,
            price_per_unit=5,
            expiration_date=timezone.now().date(),
        )
        self.assertIn("SUPPLY", str(tx))


class DishModelTest(TestCase):
    def test_str(self):
        dt = DishType.objects.create(name="Soup")
        dish = Dish.objects.create(
            name="Tomato Soup",
            description="Classic",
            price=5,
            dish_type=dt,
        )
        self.assertEqual(str(dish), "Tomato Soup")


class DishIngredientModelTest(TestCase):
    def test_unique_together(self):
        dt = DishType.objects.create(name="Main")
        dish = Dish.objects.create(
            name="Pizza",
            description="Cheese pizza",
            price=10,
            dish_type=dt,
        )
        ing = Ingredient.objects.create(name="Cheese", unit="kg")
        DishIngredient.objects.create(dish=dish, ingredient=ing, amount_required=1)
        with self.assertRaises(IntegrityError):
            DishIngredient.objects.create(dish=dish, ingredient=ing, amount_required=1)

    def test_str(self):
        dt = DishType.objects.create(name="Main")
        dish = Dish.objects.create(name="Pasta", description="Carbonara", price=12, dish_type=dt)
        ing = Ingredient.objects.create(name="Bacon", unit="kg")
        di = DishIngredient.objects.create(dish=dish, ingredient=ing, amount_required=0.5)
        self.assertIn("Bacon", str(di))


class OrderAndOrderItemModelTest(TestCase):
    def test_order_total_price_and_str(self):
        dt = DishType.objects.create(name="Main")
        dish = Dish.objects.create(name="Pizza", description="Margarita", price=20, dish_type=dt)
        order = Order.objects.create()
        OrderItem.objects.create(order=order, dish=dish, quantity=2)
        self.assertEqual(order.total_price, 40)
        self.assertIn("Order", str(order))
        self.assertIn("Pizza", str(order.items.first()))

    def test_process_order_reduces_ingredients(self):
        dt = DishType.objects.create(name="Main")
        ing = Ingredient.objects.create(name="Flour", unit="kg", stock_amount=10)
        dish = Dish.objects.create(name="Bread", description="Loaf", price=5, dish_type=dt)
        DishIngredient.objects.create(dish=dish, ingredient=ing, amount_required=2)
        order = Order.objects.create()
        OrderItem.objects.create(order=order, dish=dish, quantity=2)
        order.process_order()
        ing.refresh_from_db()
        self.assertEqual(ing.stock_amount, 6)


class FinanceManagerTest(TestCase):
    def test_finance_calculations(self):
        chef = Chef.objects.create_user(username="chef", password="pw", salary=500)
        dt = DishType.objects.create(name="Main")
        ing = Ingredient.objects.create(name="Tomato", unit="kg", stock_amount=0)

        IngredientTransaction.objects.create(
            ingredient=ing,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=10,
            price_per_unit=2,
            expiration_date=timezone.now().date(),
        )

        dish = Dish.objects.create(name="Salad", description="Fresh", price=10, dish_type=dt)
        order = Order.objects.create()
        OrderItem.objects.create(order=order, dish=dish, quantity=3)

        fm = FinanceManager()

        self.assertGreater(fm.supply_on_stock, 0)
        self.assertGreater(fm.supply_cost, 0)
        self.assertEqual(fm.revenue, 30)
        self.assertEqual(fm.employee_costs, 500)
        self.assertEqual(fm.fixed_costs, Decimal("1000.00"))
        self.assertIsInstance(fm.net_profit, Decimal)
        self.assertIsInstance(fm.profit_with_stock, Decimal)