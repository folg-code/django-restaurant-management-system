from django.shortcuts import render
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