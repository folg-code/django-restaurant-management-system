from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from kitchen.models import Dish, DishType, Cook, Ingredient, Order, DishIngredient

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
        fields = ("name", "description","ingredients", "price","dish_type", "cooks")
        widgets = {
            "cooks": forms.CheckboxSelectMultiple(),
        }

        ingredients = forms.ModelMultipleChoiceField(
            queryset=Ingredient.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )


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
        fields = ["name", "stock", "purchase_date", "expiry_date"]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["dish", "quantity"]


class DishIngredientForm(forms.ModelForm):
    class Meta:
        model = DishIngredient
        fields = ["ingredient", "quantity"]