from django.contrib import admin
from .models import DishType, Dish, Cook


@admin.register(DishType)
class DishTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "dish_type", "price")
    list_filter = ("dish_type",)
    search_fields = ("name",)


@admin.register(Cook)
class CookAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "years_of_experience")
    search_fields = ("username", "first_name", "last_name")