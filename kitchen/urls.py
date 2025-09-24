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

urlpatterns = [
    path("", views.index, name="index"),

    path(
        "dishes/",
        views.DishListView.as_view(),
        name="dish-list",
    ),
    path(
        "dishes/<int:pk>/",
        views.DishDetailView.as_view(),
        name="dish-detail",
    ),
    path(
        "cooks/",
        views.CookListView.as_view(),
        name="cook-list",
    ),
    path(
        "cooks/<int:pk>/",
        views.CookDetailView.as_view(),
        name="cook-detail",
    ),
    path(
        "dish_types/",
        views.DishTypeListView.as_view(),
        name="dish_type-list",
    ),
]
