from django.urls import path
from kitchen.views import (
    index,
    DishTypeListView,
    DishListView,
    DishDetailView,
    CookListView,
    CookDetailView
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
        "dish_types/",
        DishTypeListView.as_view(),
        name="dish_type-list",
    ),
]
