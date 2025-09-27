from django.contrib.auth.views import LogoutView
from django.urls import path
from kitchen.views import (
    index,
    DishTypeListView,
    DishListView,
    DishDetailView,
    ChefListView,
    ChefDetailView, DishCreateView, DishDeleteView, DishUpdateView,
    ChefCreateView, ChefDeleteView, ChefUpdateView, DishTypeUpdateView,
    DishTypeDeleteView, DishTypeCreateView, toggle_assign_to_dish,
    IngredientListView, IngredientCreateView, IngredientUpdateView,
    IngredientDeleteView, OrderListView, OrderCreateView, OrderDeleteView,
    finance_dashboard, OrderUpdateView, CustomLogoutView,
    IngredientDetailView, IngredientTransactionDetailView,
    IngredientTransactionListView, IngredientTransactionCreateView,
    IngredientTransactionUpdateView, IngredientWasteCreateView,
    IngredientTransactionDeleteView
)


app_name = "kitchen"
urlpatterns = [
    path("", index, name="index"),

    path("logout/",
         LogoutView.as_view(next_page="login"),
         name="logout"
         ),
    path("logout/",
         CustomLogoutView.as_view(next_page="login"),
         name="logout"
         ),
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
        "chefs/",
        ChefListView.as_view(),
        name="chef-list",
    ),
    path(
        "chefs/<int:pk>/",
        ChefDetailView.as_view(),
        name="chef-detail",
    ),
    path(
        "chefs/create/",
        ChefCreateView.as_view(),
        name="chef-create",
    ),
    path(
        "chefs/<int:pk>/delete/",
        ChefDeleteView.as_view(),
        name="chef-delete",),
    path(
        "chefs/<int:pk>/update/",
        ChefUpdateView.as_view(),
        name="chef-update",
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
        name="dish_type-update",
        ),
    path(
        "dish_types/<int:pk>/delete/",
        DishTypeDeleteView.as_view(),
        name="dish_type-delete"
        ),
    path('dishes/<int:pk>/toggle-chef/',
         toggle_assign_to_dish,
         name='dish-toggle-chef'
         ),
    path('ingredients/',
         IngredientListView.as_view(),
         name='ingredient-list'
         ),
    path('ingredients/add/',
         IngredientCreateView.as_view(),
         name='ingredient-create'
         ),
    path('ingredients/<int:pk>/edit/',
         IngredientUpdateView.as_view(),
         name='ingredient-update'
         ),
    path('ingredients/<int:pk>/delete/',
         IngredientDeleteView.as_view(),
         name='ingredient-delete'
         ),
    path('transactions/',
         IngredientTransactionListView.as_view(),
         name='ingredienttransaction-list'
         ),
    path('transactions/create/',
         IngredientTransactionCreateView.as_view(),
         name='ingredienttransaction-create'
         ),
    path('transactions/<int:pk>/update/',
         IngredientTransactionUpdateView.as_view(),
         name='ingredienttransaction-update'
         ),
    path('transactions/<int:pk>/waste/',
         IngredientWasteCreateView.as_view(),
         name='ingredienttransaction-waste'
         ),
    path('transactions/<int:pk>/delete/',
         IngredientTransactionDeleteView.as_view(),
         name='ingredienttransaction-delete'
         ),
    path("orders/",
         OrderListView.as_view(),
         name="order-list"
         ),
    path("orders/create/",
         OrderCreateView.as_view(),
         name="order-create"
         ),
    path("orders/<int:pk>/update/",
         OrderUpdateView.as_view(),
         name="order-update"
         ),
    path("orders/<int:pk>/delete/",
         OrderDeleteView.as_view(),
         name="order-delete"
         ),
    path("ingredients/<int:pk>/",
         IngredientDetailView.as_view(),
         name="ingredient-detail"
         ),
    path("transactions/<int:pk>/",
         IngredientTransactionDetailView.as_view(),
         name="ingredienttransaction-detail"
         ),
    path("finance-dashboard/",
         finance_dashboard,
         name="finance_dashboard"
         ),
]
