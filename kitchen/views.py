from django.shortcuts import render

from django.views import generic
from django.urls import reverse_lazy, reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from kitchen.forms import DishForm, CookCreationForm, CookExperienceUpdateForm
from kitchen.models import DishType, Cook, Dish




User = get_user_model()
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

class DishTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = DishType
    fields = "__all__"
    success_url = reverse_lazy("kitchen:dish_type-list")


class DishTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = DishType
    fields = "__all__"
    success_url = reverse_lazy("kitchen:dish_type-list")


class DishTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = DishType
    success_url = reverse_lazy("kitchen:dish_type-list")


class DishListView(LoginRequiredMixin, generic.ListView):

    model = Dish
    queryset = Dish.objects.select_related("dish_type").all()
    paginate_by = 7


class DishDetailView(LoginRequiredMixin, generic.DetailView):

    model = Dish

class DishCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dish
    form_class = DishForm
    success_url = reverse_lazy("kitchen:dish-list")


class DishUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Dish
    form_class = DishForm
    success_url = reverse_lazy("kitchen:dish-list")


class DishDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Dish
    success_url = reverse_lazy("kitchen:dish-list")
class CookListView(LoginRequiredMixin, generic.ListView):

    model = Cook
    paginate_by = 7


class CookDetailView(generic.DetailView):

    model = Cook
    queryset = Cook.objects.prefetch_related("dishes__dish_type").all()

class CookCreateView(LoginRequiredMixin, generic.CreateView):
    model = User
    form_class = CookCreationForm
    template_name = "kitchen/cook_form.html"
    success_url = reverse_lazy("kitchen:cook-list")


class CookDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = User
    template_name = "kitchen/cook_confirm_delete.html"
    success_url = reverse_lazy("kitchen:cook-list")


class CookLicenseUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = CookExperienceUpdateForm
    template_name = "kitchen/cook_license_update.html"

    def get_success_url(self):
        return reverse("kitchen:cook-detail", kwargs={"pk": self.object.pk})