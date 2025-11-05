from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from kitchen.models import Chef, Dish, DishType, Ingredient, IngredientTransaction, Order, OrderItem



def sample_chef(username="chef1", password="pass123", salary=100):
    return Chef.objects.create_user(username=username, password=password, salary=salary)


def sample_dish_type(name="Main"):
    return DishType.objects.create(name=name)


def sample_dish(name="Pizza", dish_type=None, price=10):
    if not dish_type:
        dish_type = sample_dish_type()
    return Dish.objects.create(name=name, description="desc", price=price, dish_type=dish_type)


def sample_ingredient(name="Tomato", unit="kg", stock_amount=10):
    return Ingredient.objects.create(name=name, unit=unit, stock_amount=stock_amount)


def sample_order():
    return Order.objects.create()


class PublicAccessTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_required_for_protected_views(self):
        protected_urls = [
            reverse("kitchen:chef-list"),
            reverse("kitchen:dish-list"),
            reverse("kitchen:ingredient-list"),
            reverse("kitchen:order-list"),
        ]
        for url in protected_urls:
            res = self.client.get(url)
            self.assertNotEqual(res.status_code, 200)


class ChefViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = sample_chef(username="admin")
        self.client.force_login(self.user)

    def test_chef_list_view(self):
        res = self.client.get(reverse("kitchen:chef-list"))
        self.assertContains(res, self.user.username)

    def test_chef_search(self):
        url = reverse("kitchen:chef-list") + "?field=username&query=admin"
        res = self.client.get(url)
        self.assertContains(res, "admin")

    def test_chef_detail_view(self):
        res = self.client.get(reverse("kitchen:chef-detail", args=[self.user.id]))
        self.assertContains(res, self.user.username)

    def test_chef_create_view(self):
        url = reverse("kitchen:chef-create")
        data = {
            "username": "newchef",
            "password1": "newpass123",
            "password2": "newpass123",
            "years_of_experience": 5,
            "salary": 200,
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Chef.objects.filter(username="newchef").exists())

    def test_chef_update_view(self):
        url = reverse("kitchen:chef-update", args=[self.user.id])
        data = {"first_name": "Updated", "last_name": "Name",
                "years_of_experience": 10, "salary": 300}
        self.client.post(url, data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_chef_delete_view(self):
        chef = sample_chef(username="tempchef")
        url = reverse("kitchen:chef-delete", args=[chef.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Chef.objects.filter(id=chef.id).exists())


class DishTypeViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = sample_chef(username="chef")
        self.client.force_login(self.user)
        self.dish_type = sample_dish_type()

    def test_dish_type_list_view(self):
        res = self.client.get(reverse("kitchen:dish_type-list"))
        self.assertContains(res, self.dish_type.name)

    def test_dish_type_search(self):
        url = reverse("kitchen:dish_type-list") + "?field=name&query=Main"
        res = self.client.get(url)
        self.assertContains(res, "Main")

    def test_dish_type_detail_view(self):
        res = self.client.get(reverse("kitchen:dish_type-detail", args=[self.dish_type.id]))
        self.assertContains(res, self.dish_type.name)

    def test_dish_type_create_view(self):
        url = reverse("kitchen:dish_type-create")
        data = {"name": "Dessert"}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(DishType.objects.filter(name="Dessert").exists())

    def test_dish_type_update_view(self):
        url = reverse("kitchen:dish_type-update", args=[self.dish_type.id])
        data = {"name": "UpdatedType"}
        self.client.post(url, data)
        self.dish_type.refresh_from_db()
        self.assertEqual(self.dish_type.name, "UpdatedType")

    def test_dish_type_delete_view(self):
        dt = sample_dish_type(name="TempType")
        url = reverse("kitchen:dish_type-delete", args=[dt.id])
        self.client.post(url)
        self.assertFalse(DishType.objects.filter(id=dt.id).exists())


class DishViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = sample_chef(username="chef")
        self.client.force_login(self.user)
        self.dish_type = sample_dish_type()
        self.dish = sample_dish(dish_type=self.dish_type)

    def test_dish_list_view(self):
        res = self.client.get(reverse("kitchen:dish-list"))
        self.assertContains(res, self.dish.name)

    def test_dish_search(self):
        url = reverse("kitchen:dish-list") + "?field=name&query=Pizza"
        res = self.client.get(url)
        self.assertContains(res, "Pizza")

    def test_dish_detail_view(self):
        res = self.client.get(reverse("kitchen:dish-detail", args=[self.dish.id]))
        self.assertContains(res, self.dish.name)

    def test_dish_create_view(self):
        url = reverse("kitchen:dish-create")
        data = {
            "name": "Soup",
            "description": "Hot soup",
            "price": 15,
            "dish_type": self.dish_type.id,
            "chefs": [self.user.id],
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Dish.objects.filter(name="Soup").exists())

    def test_dish_update_view(self):
        url = reverse("kitchen:dish-update", args=[self.dish.id])
        data = {
            "name": "Updated Pizza",
            "description": self.dish.description,
            "price": self.dish.price,
            "dish_type": self.dish_type.id,
            "chefs": [self.user.id],

            # pola wymagane przez inline formset dla DishIngredient
            "dishingredient_set-TOTAL_FORMS": "0",
            "dishingredient_set-INITIAL_FORMS": "0",
            "dishingredient_set-MIN_NUM_FORMS": "0",
            "dishingredient_set-MAX_NUM_FORMS": "1000",
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 302, res.content.decode())

        self.dish.refresh_from_db()
        self.assertEqual(self.dish.name, "Updated Pizza")

    def test_dish_delete_view(self):
        dish = sample_dish(name="TempDish", dish_type=self.dish_type)
        url = reverse("kitchen:dish-delete", args=[dish.id])
        self.client.post(url)
        self.assertFalse(Dish.objects.filter(id=dish.id).exists())


class IngredientViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = sample_chef(username="chef")
        self.client.force_login(self.user)
        self.ing = sample_ingredient()

    def test_ingredient_list_view(self):
        res = self.client.get(reverse("kitchen:ingredient-list"))
        self.assertContains(res, self.ing.name)

    def test_ingredient_search(self):
        url = reverse("kitchen:ingredient-list") + "?field=name&query=Tomato"
        res = self.client.get(url)
        self.assertContains(res, "Tomato")

    def test_ingredient_create_view(self):
        url = reverse("kitchen:ingredient-create")
        data = {"name": "Cheese", "unit": "kg", "stock_amount": 5}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Ingredient.objects.filter(name="Cheese").exists())

    def test_ingredient_update_view(self):
        url = reverse("kitchen:ingredient-update", args=[self.ing.id])
        data = {"name": "Updated Ing", "unit": "kg", "stock_amount": 10}
        self.client.post(url, data)
        self.ing.refresh_from_db()
        self.assertEqual(self.ing.name, "Updated Ing")

    def test_ingredient_delete_view(self):
        ing = sample_ingredient(name="TempIng")
        url = reverse("kitchen:ingredient-delete", args=[ing.id])
        self.client.post(url)
        self.assertFalse(Ingredient.objects.filter(id=ing.id).exists())


class IngredientTransactionViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = sample_chef(username="chef")
        self.client.force_login(self.user)
        self.ing = sample_ingredient()
        self.transaction = IngredientTransaction.objects.create(
            ingredient=self.ing,
            transaction_type=IngredientTransaction.SUPPLY,
            quantity=5,
            price_per_unit=2,
            expiration_date=timezone.now().date(),
        )

    def test_transaction_list_view(self):
        res = self.client.get(reverse("kitchen:ingredienttransaction-list"))
        self.assertContains(res, self.ing.name)

    def test_transaction_search(self):
        url = reverse("kitchen:ingredienttransaction-list") + "?field=ingredient__name&query=Tomato"
        res = self.client.get(url)
        self.assertContains(res, "Tomato")

    def test_transaction_detail_view(self):
        res = self.client.get(reverse("kitchen:ingredienttransaction-detail", args=[self.transaction.id]))
        self.assertContains(res, self.ing.name)

    def test_transaction_create_view(self):
        url = reverse("kitchen:ingredienttransaction-create")
        data = {
            "ingredient": self.ing.id,
            "transaction_type": IngredientTransaction.SUPPLY,
            "quantity": 10,
            "price_per_unit": 3,
            "expiration_date": timezone.now().date(),
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(self.ing.transactions.count(), 2)

    def test_transaction_update_view(self):
        url = reverse("kitchen:ingredienttransaction-update", args=[self.transaction.id])
        data = {
            "ingredient": self.ing.id,
            "transaction_type": IngredientTransaction.SUPPLY,
            "quantity": 7,
            "price_per_unit": 4,
            "expiration_date": timezone.now().date(),
        }
        self.client.post(url, data)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.quantity, 7)

    def test_transaction_delete_view(self):
        url = reverse("kitchen:ingredienttransaction-delete", args=[self.transaction.id])
        self.client.post(url)
        self.assertFalse(IngredientTransaction.objects.filter(id=self.transaction.id).exists())


class OrderViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = sample_chef(username="chef")
        self.client.force_login(self.user)
        self.dish = sample_dish()

    def test_order_list_view(self):
        order = sample_order()
        OrderItem.objects.create(order=order, dish=self.dish, quantity=1)
        res = self.client.get(reverse("kitchen:order-list"))
        self.assertContains(res, str(order.id))
        self.assertContains(res, self.dish.name)

    def test_order_search(self):
        order = sample_order()
        OrderItem.objects.create(order=order, dish=self.dish, quantity=1)
        url = reverse("kitchen:order-list") + f"?field=id&query={order.id}"
        res = self.client.get(url)
        self.assertContains(res, str(order.id))
        self.assertContains(res, self.dish.name)

    def test_order_detail_view(self):
        order = sample_order()
        OrderItem.objects.create(order=order, dish=self.dish, quantity=2)
        res = self.client.get(reverse("kitchen:order-detail", args=[order.id]))
        self.assertContains(res, self.dish.name)

    def test_order_create_view(self):
        url = reverse("kitchen:order-create")
        data = {
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-dish": str(self.dish.id),
            "items-0-quantity": "1",
            "items-0-DELETE": "",
        }
        res = self.client.post(url, data)
        print(res.content.decode())
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)



