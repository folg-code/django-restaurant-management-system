from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory

from kitchen.models import Dish, DishType, Cook, Ingredient, Order, DishIngredient, OrderItem

User = get_user_model()


class CookCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "years_of_experience",)




class CookExperienceUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("years_of_experience",)



class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ("name", "description", "price", "dish_type", "cooks")
        widgets = {
            "cooks": forms.CheckboxSelectMultiple(),
        }


class CookSearchForm(forms.Form):
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search by username"}),
    )


class DishSearchForm(forms.Form):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )


class DishTypeSearchForm(forms.Form):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search by name"}),
    )

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "stock_amount", "purchase_date", "expiration_date"]





class DishIngredientForm(forms.ModelForm):
    class Meta:
        model = DishIngredient
        fields = ["ingredient", "amount_required"]


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['dish', 'quantity']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = []


DishIngredientFormSet = inlineformset_factory(
    Dish,
    DishIngredient,
    fields=['ingredient', 'amount_required'],
    extra=1,
    can_delete=True
)



OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True
)