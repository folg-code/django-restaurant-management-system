from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.forms import ValidationError

from kitchen.forms import (
    ChefCreationForm,
    ChefUpdateForm,
    DishForm,
    ChefSearchForm,
    DishSearchForm,
    DishTypeSearchForm,
    IngredientForm,
    IngredientSearchForm,
    IngredientTransactionForm,
    IngredientWasteForm,
    DishIngredientForm,
    OrderItemForm,
    OrderForm,
    OrderSearchForm,
    IngredientTransactionSearchForm, OrderItemFormSet, DishIngredientFormSet,
)
from kitchen.models import (
    Dish, DishType, Ingredient, IngredientTransaction,
    DishIngredient, Order, OrderItem
)


User = get_user_model()


class ChefFormTests(TestCase):
    def test_chef_creation_form_valid(self):
        form = ChefCreationForm(data={
            "username": "chef1",
            "first_name": "John",
            "last_name": "Doe",
            "years_of_experience": 5,
            "salary": 3000,
            "password1": "testpass123",
            "password2": "testpass123",
        })
        self.assertTrue(form.is_valid())

    def test_chef_update_form(self):
        chef = User.objects.create_user(
            username="chef2", password="pass"
        )
        form = ChefUpdateForm(instance=chef, data={
            "first_name": "Jane",
            "last_name": "Smith",
            "years_of_experience": 3,
            "salary": 2500,
        })
        self.assertTrue(form.is_valid())


class DishFormTests(TestCase):
    def test_dish_form_with_multiple_chefs(self):
        dish_type = DishType.objects.create(name="Pizza")
        chef1 = User.objects.create_user(username="chef1", password="123")
        chef2 = User.objects.create_user(username="chef2", password="123")

        form = DishForm(data={
            "name": "Margherita",
            "description": "Classic",
            "price": 25,
            "dish_type": dish_type.id,
            "chefs": [chef1.id, chef2.id],
        })
        self.assertTrue(form.is_valid())


class SearchFormsTests(TestCase):
    def test_chef_search_form(self):
        form = ChefSearchForm(data={"field": "username", "query": "john"})
        self.assertTrue(form.is_valid())

    def test_dish_search_form(self):
        form = DishSearchForm(data={"field": "name", "query": "Pizza"})
        self.assertTrue(form.is_valid())

    def test_dish_type_search_form(self):
        form = DishTypeSearchForm(data={"name": "Soup"})
        self.assertTrue(form.is_valid())

    def test_ingredient_search_form(self):
        form = IngredientSearchForm(data={"field": "name", "query": "Tomato"})
        self.assertTrue(form.is_valid())

    def test_order_search_form(self):
        form = OrderSearchForm(data={"field": "id", "query": "1"})
        self.assertTrue(form.is_valid())

    def test_transaction_search_form(self):
        form = IngredientTransactionSearchForm(
            data={"field": "transaction_type", "query": "SUPPLY"}
        )
        self.assertTrue(form.is_valid())


class IngredientFormTests(TestCase):
    def test_ingredient_form(self):
        form = IngredientForm(data={
            "name": "Tomato",
            "unit": "kg",
            "stock_amount": 10,
        })
        self.assertTrue(form.is_valid())


class IngredientTransactionFormTests(TestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name="Cheese", unit="kg", stock_amount=5
        )

    def test_supply_requires_expiration_date(self):
        form = IngredientTransactionForm(data={
            "ingredient": self.ingredient.id,
            "transaction_type": IngredientTransaction.SUPPLY,
            "quantity": 2,
            "price_per_unit": 10,
            "expiration_date": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Expiration date is required", str(form.errors))

    def test_waste_cannot_exceed_stock(self):
        form = IngredientTransactionForm(data={
            "ingredient": self.ingredient.id,
            "transaction_type": IngredientTransaction.WASTE,
            "quantity": 10,
            "price_per_unit": 0,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Cannot waste more", str(form.errors))

    def test_valid_supply(self):
        form = IngredientTransactionForm(data={
            "ingredient": self.ingredient.id,
            "transaction_type": IngredientTransaction.SUPPLY,
            "quantity": 2,
            "price_per_unit": 5,
            "expiration_date": timezone.now().date(),
        })
        self.assertTrue(form.is_valid())


class IngredientWasteFormTests(TestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name="Milk", unit="L", stock_amount=10
        )
        self.supply = IngredientTransaction.objects.create(
            ingredient=self.ingredient,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=10,
            price_per_unit=2,
            expiration_date=timezone.now().date()
        )

        self.data = {
            'quantity': 5,
            'note': 'some waste',
            'selected': True,
            'supply_transaction_id': self.supply.id,
        }

    def test_waste_form_inherits_supply_instance(self):
        form = IngredientWasteForm(data=self.data, supply_instance=self.supply)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.fields['available_quantity'].initial, 10)


class DishIngredientFormTests(TestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name="Flour", unit="kg", stock_amount=100
        )

    def test_dish_ingredient_form(self):
        form = DishIngredientForm(data={
            "ingredient": self.ingredient.id,
            "amount_required": 1.5,
        })
        self.assertTrue(form.is_valid())


class OrderFormsTests(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(name="Main")
        self.dish = Dish.objects.create(
            name="Pasta", description="Yummy", price=30, dish_type=self.dish_type
        )
        self.order = Order.objects.create()

    def test_order_item_form(self):
        form = OrderItemForm(data={"dish": self.dish.id, "quantity": 2})
        self.assertTrue(form.is_valid())

    def test_order_form(self):
        form = OrderForm(data={})
        self.assertTrue(form.is_valid())

class DishIngredientFormSetTests(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(name="Main")
        self.dish = Dish.objects.create(
            name="Burger", description="Tasty", price=15, dish_type=self.dish_type
        )
        self.ingredient1 = Ingredient.objects.create(
            name="Bun", unit="pcs", stock_amount=50
        )
        self.ingredient2 = Ingredient.objects.create(
            name="Meat", unit="kg", stock_amount=20
        )

    def test_valid_formset(self):
        formset = DishIngredientFormSet(
            instance=self.dish,
            data={
                "dishingredient_set-TOTAL_FORMS": "2",
                "dishingredient_set-INITIAL_FORMS": "0",
                "dishingredient_set-MIN_NUM_FORMS": "0",
                "dishingredient_set-MAX_NUM_FORMS": "1000",
                "dishingredient_set-0-ingredient": self.ingredient1.id,
                "dishingredient_set-0-amount_required": 1,
                "dishingredient_set-1-ingredient": self.ingredient2.id,
                "dishingredient_set-1-amount_required": 0.5,
            },
        )
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        self.assertEqual(DishIngredient.objects.filter(dish=self.dish).count(), 2)

    def test_invalid_formset_missing_ingredient(self):
        formset = DishIngredientFormSet(
            instance=self.dish,
            data={
                "dishingredient_set-TOTAL_FORMS": "1",
                "dishingredient_set-INITIAL_FORMS": "0",
                "dishingredient_set-MIN_NUM_FORMS": "0",
                "dishingredient_set-MAX_NUM_FORMS": "1000",
                "dishingredient_set-0-ingredient": "",
                "dishingredient_set-0-amount_required": 1,
            },
        )
        self.assertFalse(formset.is_valid())


class OrderItemFormSetTests(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(name="Main")
        self.dish1 = Dish.objects.create(
            name="Pizza", description="Cheesy", price=20, dish_type=self.dish_type
        )
        self.dish2 = Dish.objects.create(
            name="Pasta", description="Yummy", price=18, dish_type=self.dish_type
        )
        self.order = Order.objects.create()

    def test_valid_order_item_formset(self):
        formset_data = {
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-dish": str(self.dish1.id),
            "items-0-quantity": "2",
            "items-1-dish": str(self.dish2.id),
            "items-1-quantity": "1",
        }

        formset = OrderItemFormSet(data=formset_data, instance=self.order, prefix="items")
        self.assertTrue(formset.is_valid(), formset.non_form_errors())
        formset.save()
        self.assertEqual(OrderItem.objects.filter(order=self.order).count(), 2)

    def test_invalid_order_item_formset_quantity_required(self):
        data = {
            "orderitem_set-TOTAL_FORMS": "1",
            "orderitem_set-INITIAL_FORMS": "0",
            "orderitem_set-MIN_NUM_FORMS": "0",
            "orderitem_set-MAX_NUM_FORMS": "1000",
            "orderitem_set-0-dish": str(self.dish1.id),
            "orderitem_set-0-quantity": "",
        }
        formset = OrderItemFormSet(data, instance=self.order)
        self.assertFalse(formset.is_valid())