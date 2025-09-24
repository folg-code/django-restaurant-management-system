from django.shortcuts import render

from django.views import generic
from kitchen.models import DishType, Cook, Dish

# Create your views here.
def index(request):
    num_dish_type = DishType.objects.count()
    num_cook = Cook.objects.count()
    num_dish = Dish.objects.count()

    context = {
        "num_dish_type": num_dish_type,
        "num_cook": num_cook,
        "num_dish": num_dish,
    }

    return render(request, "kitchen/index.html", context)

class DishTypeListView(generic.ListView):

    model = DishType
    queryset = DishType.objects.all().order_by("name")
    paginate_by = 7


class DishListView(generic.ListView):

    model = Dish
    queryset = Dish.objects.select_related("dish_type").all()
    paginate_by = 7


class DishDetailView(generic.DetailView):

    model = Dish


class CookListView(generic.ListView):

    model = Cook
    paginate_by = 7


class CookDetailView(generic.DetailView):

    model = Cook
    queryset = Cook.objects.prefetch_related("dish__dish_type").all()