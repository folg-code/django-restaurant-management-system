from django.urls import path
from kitchen.views import (
    index,
    DishTypeListView,
    DishListView,
    DishDetailView,
    CookListView,
    CookDetailView, DishCreateView, DishDeleteView, DishUpdateView, CookCreateView, CookDeleteView,
    CookUpdateView, DishTypeUpdateView, DishTypeDeleteView, DishTypeCreateView,
    toggle_assign_to_dish, IngredientListView, IngredientCreateView, IngredientUpdateView, IngredientDeleteView,
    OrderListView, OrderCreateView, OrderDeleteView, finance_dashboard, OrderUpdateView
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
        CookUpdateView.as_view(),
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

    path('ingredients/', views.IngredientListView.as_view(), name='ingredient-list'),
    path('ingredients/add/', views.IngredientCreateView.as_view(), name='ingredient-create'),
    path('ingredients/<int:pk>/edit/', views.IngredientUpdateView.as_view(), name='ingredient-update'),
    path('ingredients/<int:pk>/delete/', views.IngredientDeleteView.as_view(), name='ingredient-delete'),

    path('transactions/', views.IngredientTransactionListView.as_view(), name='ingredienttransaction-list'),
    path('transactions/create/', views.IngredientTransactionCreateView.as_view(), name='ingredienttransaction-create'),
    path('transactions/<int:pk>/update/', views.IngredientTransactionUpdateView.as_view(),
         name='ingredienttransaction-update'),

    path('transactions/<int:pk>/waste/',
     views.IngredientWasteCreateView.as_view(),
     name='ingredienttransaction-waste'),
    path('transactions/<int:pk>/delete/', views.IngredientTransactionDeleteView.as_view(),
         name='ingredienttransaction-delete'),

    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),

    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order-update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order-delete"),


    path("finance-dashboard/", views.finance_dashboard, name="finance_dashboard"),

]
