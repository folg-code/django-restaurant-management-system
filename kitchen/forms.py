from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory

from kitchen.models import Dish, DishType, Cook, Ingredient, Order, DishIngredient, OrderItem, IngredientTransaction

User = get_user_model()


class CookCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "years_of_experience",)




class CookUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name","years_of_experience", "salary")



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
        fields = ["name", "unit"]


class IngredientTransactionForm(forms.ModelForm):
    class Meta:
        model = IngredientTransaction
        fields = ['ingredient', 'transaction_type', 'quantity', 'price_per_unit', 'expiration_date', 'note']
        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'transaction_type': forms.Select(),
            'note': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        t_type = cleaned_data.get('transaction_type')
        exp_date = cleaned_data.get('expiration_date')
        qty = cleaned_data.get('quantity')
        ingredient = cleaned_data.get('ingredient')

        if t_type == IngredientTransaction.SUPPLY and not exp_date:
            raise forms.ValidationError("Expiration date is required for supply transactions")

        if t_type == IngredientTransaction.WASTE and ingredient and qty:
            if qty > ingredient.stock_amount:
                raise forms.ValidationError("Cannot waste more than available stock")
        return cleaned_data

class IngredientWasteForm(forms.ModelForm):
    supply_transaction_id = forms.IntegerField(widget=forms.HiddenInput)
    available_quantity = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'readonly': 'readonly'})
    )
    selected = forms.BooleanField(required=False, label="Waste from this supply?")
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = IngredientTransaction
        fields = ['quantity', 'note']

    def __init__(self, *args, **kwargs):
        self.supply_instance = kwargs.pop('supply_instance', None)
        super().__init__(*args, **kwargs)

        if self.supply_instance:
            self.fields['quantity'].widget.attrs['max'] = self.supply_instance.quantity
            self.fields['quantity'].widget.attrs['placeholder'] = f"Max {self.supply_instance.quantity}"
            self.fields['available_quantity'].initial = self.supply_instance.quantity
            self.fields['supply_transaction_id'].initial = self.supply_instance.pk


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