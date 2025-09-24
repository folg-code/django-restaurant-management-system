from django.shortcuts import render

from django.views import generic
from kitchen.models import DishType, Cook, Dish

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

@login_required
def index(request):
    num_dish_type = DishType.objects.count()
    num_cook = Cook.objects.count()
    num_dish = Dish.objects.count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_dish_type": num_dish_type,
        "num_cook": num_cook,
        "num_dish": num_dish,
        "num_visits": num_visits + 1
    }

    return render(request, "kitchen/index.html", context)

class DishTypeListView(LoginRequiredMixin, generic.ListView):

    model = DishType
    queryset = DishType.objects.all().order_by("name")
    paginate_by = 7


class DishListView(LoginRequiredMixin, generic.ListView):

    model = Dish
    queryset = Dish.objects.select_related("dish_type").all()
    paginate_by = 7


class DishDetailView(LoginRequiredMixin, generic.DetailView):

    model = Dish


class CookListView(LoginRequiredMixin, generic.ListView):

    model = Cook
    paginate_by = 7


class CookDetailView(generic.DetailView):

    model = Cook
    queryset = Cook.objects.prefetch_related("dishes__dish_type").all()