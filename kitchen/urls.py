from django.urls import path
from kitchen.views import (
    index,
    DishTypeListView,
    DishListView,
    DishDetailView,
    CookListView,
    CookDetailView, DishCreateView, DishDeleteView, DishUpdateView, CookCreateView, CookDeleteView,
    CookExperienceUpdateView, DishTypeUpdateView, DishTypeDeleteView, DishTypeCreateView,
    toggle_assign_to_dish
)

from . import views
from .views import index


app_name = "kitchen"
urlpatterns = [
    path("", index, name="index"),

    path(
        "dishes/",
        DishListView.as_view(),
        name="dish-list",
    ),
    path(
        "dishes/<int:pk>/",
        DishDetailView.as_view(),
        name="dish-detail",
    ),
    path(
        "dishes/create/",
        DishCreateView.as_view(),
        name="dish-create",
    ),
    path(
        "dishes/<int:pk>/delete/",
        DishDeleteView.as_view(),
        name="dish-delete",
    ),
    path(
        "dishes/<int:pk>/update/",
        DishUpdateView.as_view(),
        name="dish-update",
    ),
    path(
        "dishes/<int:pk>/toggle-assign/",
        toggle_assign_to_dish,
        name="toggle-dish-assign",
    ),
    path(
        "cooks/",
        CookListView.as_view(),
        name="cook-list",
    ),
    path(
        "cooks/<int:pk>/",
        CookDetailView.as_view(),
        name="cook-detail",
    ),
    path(
        "cooks/create/",
        CookCreateView.as_view(),
        name="cook-create",
    ),
    path(
        "cooks/<int:pk>/delete/",
        CookDeleteView.as_view(),
        name="cook-delete",),
    path(
        "cooks/<int:pk>/update/",
        CookExperienceUpdateView.as_view(),
        name="cook-update",
    ),
    path(
        "dish_types/",
        DishTypeListView.as_view(),
        name="dish_type-list",
    ),
    path(
        "dish_types/create/",
        DishTypeCreateView.as_view(),
        name="dish_type-create",
    ),
    path(
        "dish_types/<int:pk>/update/",
        DishTypeUpdateView.as_view(),
        name="dish_type-update",),
    path(
        "dish_types/<int:pk>/delete/",
         DishTypeDeleteView.as_view(),
         name="dish_type-delete"
        ),

    path('dishes/<int:pk>/toggle-cook/', views.toggle_assign_to_dish, name='dish-toggle-cook'),


]
