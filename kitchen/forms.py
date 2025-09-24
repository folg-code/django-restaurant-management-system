from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from kitchen.models import Dish, DishType, Cook

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
        fields = ("name", "dish_type", "cooks")  # include drivers field
        widgets = {
            "cooks": forms.CheckboxSelectMultiple(),  # <-- use checkboxes
        }