from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy, reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from kitchen.forms import DishForm, CookCreationForm, CookExperienceUpdateForm, CookSearchForm, DishTypeSearchForm, \
    DishSearchForm
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
    template_name = "kitchen/dishtype_list.html"
    context_object_name = "dish_type_list"
    queryset = DishType.objects.all().order_by("name")
    paginate_by = 7

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DishTypeListView, self).get_context_data(**kwargs)
        context["search_form"] = DishTypeSearchForm(self.request.GET)
        return context

    def get_queryset(self):
        name = self.request.GET.get("name")
        queryset = super().get_queryset()
        if name:
            return DishType.objects.filter(name__icontains=name)
        return queryset

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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DishListView, self).get_context_data(**kwargs)
        context["search_form"] = DishSearchForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = (Dish.
                    objects.
                    select_related("dish_type").
                    order_by("name"))
        model = self.request.GET.get("name")
        if model:
            queryset = queryset.filter(model__icontains=model)
        return queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CookListView, self).get_context_data(**kwargs)
        context["search_form"] = CookSearchForm(self.request.GET)
        return context

    def get_queryset(self):
        username = self.request.GET.get("username")
        queryset = super().get_queryset()
        if username:
            return Cook.objects.filter(username__icontains=username)
        return queryset.order_by("username")


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


class CookExperienceUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = CookExperienceUpdateForm
    template_name = "kitchen/cook_experience_update.html"

    def get_success_url(self):
        return reverse("kitchen:cook-detail", kwargs={"pk": self.object.pk})

@login_required
def toggle_assign_to_dish(request, pk):
    cook = Cook.objects.get(id=request.user.id)
    if (
        Dish.objects.get(id=pk) in cook.dishes.all()
    ):
        cook.dishes.remove(pk)
    else:
        cook.dishes.add(pk)
    return HttpResponseRedirect(reverse_lazy("kitchen:dish-detail", args=[pk]))