from decimal import Decimal

from django.db import transaction
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy, reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from kitchen.forms import DishForm, CookCreationForm, CookUpdateForm, CookSearchForm, DishTypeSearchForm, \
    DishSearchForm, IngredientForm, OrderForm, DishIngredientFormSet, OrderItemFormSet
from kitchen.models import DishType, Cook, Dish, Ingredient, Order, OrderItem, FinanceManager

User = get_user_model()
@login_required
def index(request):
    num_dish_type = DishType.objects.count()
    num_cook = Cook.objects.count()
    num_dish = Dish.objects.count()
    num_orders = Order.objects.count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_dish_type": num_dish_type,
        "num_cook": num_cook,
        "num_dish": num_dish,
        "num_orders": num_orders,
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
        name = self.request.GET.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class DishDetailView(LoginRequiredMixin, generic.DetailView):

    model = Dish

class DishCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dish
    form_class = DishForm
    template_name = "kitchen/dish_form.html"
    success_url = reverse_lazy("kitchen:dish-list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["ingredients"] = DishIngredientFormSet(self.request.POST)
        else:
            data["ingredients"] = DishIngredientFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ingredients = context["ingredients"]
        self.object = form.save()
        if ingredients.is_valid():
            ingredients.instance = self.object
            ingredients.save()
        return super().form_valid(form)


class DishUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Dish
    form_class = DishForm
    template_name = 'kitchen/dish_form.html'
    success_url = reverse_lazy("kitchen:dish-list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['ingredients'] = DishIngredientFormSet(self.request.POST, instance=self.object)
        else:
            data['ingredients'] = DishIngredientFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        ingredients = context['ingredients']
        if form.is_valid() and ingredients.is_valid():
            self.object = form.save()
            ingredients.instance = self.object
            ingredients.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


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


class CookUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = CookUpdateForm
    template_name = "kitchen/cook_form.html"

    def get_success_url(self):
        return reverse("kitchen:cook-detail", kwargs={"pk": self.object.pk})


class IngredientListView(LoginRequiredMixin, generic.ListView):
    model = Ingredient
    template_name = "kitchen/ingredient_list.html"
    context_object_name = "ingredient_list"


class IngredientCreateView(LoginRequiredMixin, generic.CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "kitchen/ingredient_form.html"
    success_url = reverse_lazy("kitchen:ingredient-list")


class IngredientUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "kitchen/ingredient_form.html"
    success_url = reverse_lazy("kitchen:ingredient-list")


class IngredientDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Ingredient
    template_name = "kitchen/ingredient_confirm_delete.html"
    success_url = reverse_lazy("kitchen:ingredient-list")


class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = "kitchen/order_list.html"
    context_object_name = "order_list"
    paginate_by = 10


class OrderCreateView(LoginRequiredMixin, generic.CreateView):
    model = Order
    form_class = OrderForm
    template_name = "kitchen/order_form.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = OrderItemFormSet(self.request.POST)
        else:
            data['items'] = OrderItemFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']

        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()

                for order_item in self.object.items.all():
                    dish = order_item.dish
                    quantity = order_item.quantity
                    for di in dish.dishingredient_set.all():
                        ingredient = di.ingredient
                        ingredient.stock_amount -= di.amount_required * quantity
                        if ingredient.stock_amount < 0:
                            ingredient.stock_amount = 0
                        ingredient.save()
        return redirect('kitchen:order-list')

class OrderUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "kitchen/order_form.html"
    success_url = reverse_lazy("kitchen:order-list")
class OrderDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Order
    template_name = "kitchen/order_confirm_delete.html"
    success_url = reverse_lazy("kitchen:order-list")


def finance_dashboard(request):
    fm = FinanceManager()

    print("SUPPLY ON STOCK:", fm.supply_on_stock)

    context = {
        "supply_on_stock": fm.supply_on_stock,
        "supply_cost": fm.supply_cost,
        "revenue": fm.revenue,
        "employee_costs": fm.employee_costs,
        "fixed_costs": fm.fixed_costs,
        "profit": fm.profit,
    }
    return render(request, "kitchen/finance_dashboard.html", context)


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

