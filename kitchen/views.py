

from django import forms
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.db import transaction
from django.forms import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic, View
from django.urls import reverse_lazy, reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model


from kitchen.forms import (
    DishForm, DishSearchForm, ChefCreationForm, ChefUpdateForm, ChefSearchForm,
    DishTypeSearchForm, IngredientForm, OrderForm, DishIngredientFormSet,
    OrderItemFormSet, IngredientTransactionForm, IngredientWasteForm,
    IngredientSearchForm, OrderSearchForm, IngredientTransactionSearchForm)
from kitchen.models import (
    DishType, Chef, Dish, Ingredient,
    Order, FinanceManager, IngredientTransaction)

User = get_user_model()


@login_required
def index(request):
    num_dish_type = DishType.objects.count()
    num_chef = Chef.objects.count()
    num_dish = Dish.objects.count()
    num_orders = Order.objects.count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_dish_type": num_dish_type,
        "num_chef": num_chef,
        "num_dish": num_dish,
        "num_orders": num_orders,
        "num_visits": num_visits + 1
    }

    return render(request, "kitchen/index.html", context)


class DishTypeListView(LoginRequiredMixin, generic.ListView):
    print(DishType.objects.all())
    print(DishType.objects.count())
    model = DishType
    template_name = "kitchen/dishtype_list.html"
    context_object_name = "dish_type_list"
    queryset = DishType.objects.all().order_by("name")
    paginate_by = 5

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
    template_name = "kitchen/dish_list.html"
    context_object_name = "dish_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = DishSearchForm(self.request.GET)

        if self.form.is_valid():
            field = self.form.cleaned_data.get('field') or 'name'
            query = self.form.cleaned_data.get('query', '')

            allowed_fields = ['name', 'description',
                              'price', 'dish_type__name']
            if field in allowed_fields and query:
                kwargs = (
                    {f"{field}__icontains": query}
                    if '__' not in field
                    else {f"{field}__icontains": query}
                )
                queryset = queryset.filter(**kwargs)

        sort_field = self.request.GET.get('sort', 'name')
        sort_dir = self.request.GET.get('dir', 'asc')
        allowed_sort_fields = ['name', 'price', 'dish_type__name']
        if sort_field in allowed_sort_fields:
            if sort_dir == 'desc':
                sort_field = f"-{sort_field}"
            queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form
        context['current_sort_field'] = self.request.GET.get('sort', 'name')
        context['current_sort_dir'] = self.request.GET.get('dir', 'asc')
        context['allowed_fields'] = ['name', 'price', 'dish_type__name']
        return context


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
            data['ingredients'] = DishIngredientFormSet(self.request.POST,
                                                        instance=self.object)
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


class ChefListView(generic.ListView):
    model = Chef
    template_name = "kitchen/chef_list.html"
    context_object_name = "chef_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = ChefSearchForm(self.request.GET)

        if self.form.is_valid():
            field = self.form.cleaned_data.get('field') or 'username'
            query = self.form.cleaned_data.get('query', '')

            allowed_fields = ['username', 'email',
                              'years_of_experience', 'salary']
            if field in allowed_fields and query:
                if field in ['years_of_experience', 'salary']:
                    try:
                        queryset = queryset.filter(**{f"{field}": query})
                    except ValueError:
                        queryset = queryset.none()
                else:
                    queryset = (queryset.
                                filter(**{f"{field}__icontains": query}))

        sort_field = self.request.GET.get('sort', 'username')
        sort_dir = self.request.GET.get('dir', 'asc')
        allowed_sort_fields = ['username', 'email',
                               'years_of_experience', 'salary', 'id']
        if sort_field in allowed_sort_fields:
            if sort_dir == 'desc':
                sort_field = f"-{sort_field}"
            queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form
        context['current_sort_field'] = self.request.GET.get('sort',
                                                             'username')
        context['current_sort_dir'] = self.request.GET.get('dir', 'asc')
        return context


class ChefDetailView(generic.DetailView):

    model = Chef
    queryset = Chef.objects.prefetch_related("dishes__dish_type").all()


class ChefCreateView(LoginRequiredMixin, generic.CreateView):
    model = User
    form_class = ChefCreationForm
    template_name = "kitchen/chef_form.html"
    success_url = reverse_lazy("kitchen:chef-list")


class ChefDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = User
    template_name = "kitchen/chef_confirm_delete.html"
    success_url = reverse_lazy("kitchen:chef-list")


class ChefUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = ChefUpdateForm
    template_name = "kitchen/chef_form.html"

    def get_success_url(self):
        return reverse("kitchen:chef-detail", kwargs={"pk": self.object.pk})


class IngredientListView(generic.ListView):
    model = Ingredient
    template_name = "kitchen/ingredient_list.html"
    context_object_name = "ingredient_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = IngredientSearchForm(self.request.GET)

        if self.form.is_valid():
            field = self.form.cleaned_data.get('field') or 'name'
            query = self.form.cleaned_data.get('query', '')

            allowed_fields = ['id', 'name', 'unit',
                              'stock_amount', 'price_per_unit']
            if field in allowed_fields and query:
                kwargs = {f"{field}__icontains": query}
                queryset = queryset.filter(**kwargs)

        sort_field = self.request.GET.get('sort', 'id')
        sort_dir = self.request.GET.get('dir', 'asc')
        if sort_field in ['id', 'name', 'unit',
                          'stock_amount', 'price_per_unit']:
            if sort_dir == 'desc':
                sort_field = f"-{sort_field}"
            queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form
        context['current_sort_field'] = self.request.GET.get('sort', 'id')
        context['current_sort_dir'] = self.request.GET.get('dir', 'asc')
        context['allowed_fields'] = [
            'id',
            'name',
            'unit',
            'stock_amount',
            'price_per_unit'
        ]
        return context


class IngredientCreateView(generic.CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "kitchen/ingredient_form.html"
    success_url = reverse_lazy("kitchen:ingredient-list")


class IngredientUpdateView(generic.UpdateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "kitchen/ingredient_form.html"
    success_url = reverse_lazy("kitchen:ingredient-list")


class IngredientDeleteView(generic.DeleteView):
    model = Ingredient
    template_name = "kitchen/ingredient_confirm_delete.html"
    success_url = reverse_lazy("kitchen:ingredient-list")


class IngredientTransactionListView(generic.ListView):
    model = IngredientTransaction
    template_name = "kitchen/ingredienttransaction_list.html"
    context_object_name = "transaction_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = IngredientTransaction.objects.select_related('ingredient')

        self.form = IngredientTransactionSearchForm(self.request.GET)

        if self.form.is_valid():
            field = self.form.cleaned_data.get('field') or 'ingredient'
            query = self.form.cleaned_data.get('query', '')

            if field == 'ingredient' and query:
                queryset = queryset.filter(ingredient__name__icontains=query)
            elif field == 'transaction_type' and query:
                queryset = queryset.filter(transaction_type__icontains=query)
            elif field == 'created_at' and query:
                queryset = queryset.filter(created_at__date=query)
            elif field == 'quantity' and query:
                try:
                    queryset = queryset.filter(quantity=float(query))
                except ValueError:
                    queryset = queryset.none()

        sort_field = self.request.GET.get('sort', 'created_at')
        sort_dir = self.request.GET.get('dir', 'asc')
        allowed_sort_fields = [
            'ingredient',
            'transaction_type',
            'created_at',
            'quantity',
            'price_per_unit',
            'id'
        ]

        if sort_field in allowed_sort_fields:
            if sort_field == 'ingredient':
                queryset = (queryset.
                            order_by(f"{'-' if sort_dir=='desc' else ''}"
                                     f"ingredient__name")
                            )
            else:
                queryset = (queryset.
                            order_by(f"{'-' if sort_dir=='desc' else ''}"
                                     f"{sort_field}")
                            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form
        context['current_sort_field'] = self.request.GET.get('sort',
                                                             'created_at')
        context['current_sort_dir'] = self.request.GET.get('dir', 'asc')
        return context


class IngredientTransactionCreateView(generic.CreateView):
    model = IngredientTransaction
    form_class = IngredientTransactionForm
    template_name = "kitchen/ingredienttransaction_form.html"
    success_url = reverse_lazy("kitchen:ingredienttransaction-list")

    def get_initial(self):
        initial = super().get_initial()

        initial['transaction_type'] = IngredientTransaction.SUPPLY
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['transaction_type'].widget = forms.HiddenInput()
        return form


class IngredientWasteCreateView(View):
    template_name = "kitchen/ingredienttransaction_waste_form.html"

    def get(self, request, *args, **kwargs):
        supply_transaction = get_object_or_404(
            IngredientTransaction,
            pk=kwargs['pk'],
            transaction_type=IngredientTransaction.SUPPLY
        )
        ingredient = supply_transaction.ingredient

        supply_qs = (ingredient.
                     transactions.
                     filter(transaction_type=IngredientTransaction.SUPPLY,
                            quantity__gt=0)
                     )
        WasteFormSet = formset_factory(IngredientWasteForm, extra=0)
        formset = WasteFormSet(
            initial=[
                {'supply_transaction_id': tx.pk,
                 'available_quantity': tx.quantity
                 } for tx in supply_qs])

        for form, tx in zip(formset.forms, supply_qs):
            form.supply_instance = tx

        return render(request,
                      self.template_name,
                      {'formset': formset, 'ingredient': ingredient}
                      )

    def post(self, request, *args, **kwargs):
        print("POST data:", request.POST)
        supply_transaction = get_object_or_404(
            IngredientTransaction,
            pk=kwargs['pk'],
            transaction_type=IngredientTransaction.SUPPLY
        )
        ingredient = supply_transaction.ingredient
        supply_qs = (ingredient.
                     transactions.
                     filter(transaction_type=IngredientTransaction.SUPPLY,
                            quantity__gt=0)
                     )
        WasteFormSet = formset_factory(IngredientWasteForm, extra=0)
        formset = WasteFormSet(request.POST)

        if formset.is_valid():
            for form, tx in zip(formset.forms, supply_qs):
                qty = form.cleaned_data.get('quantity', 0)
                if qty > 0:
                    note_value = form.cleaned_data.get('note')
                    if not note_value:
                        note_value = f"Waste from supply transaction #{tx.pk}"
                    IngredientTransaction.objects.create(
                        ingredient=ingredient,
                        transaction_type=IngredientTransaction.WASTE,
                        quantity=qty,
                        note=note_value
                    )
            return redirect('kitchen:ingredienttransaction-list')
        return render(
            request,
            self.template_name,
            {
                'formset': formset,
                'ingredient': ingredient
            }
        )


class IngredientTransactionUpdateView(generic.UpdateView):
    model = IngredientTransaction
    form_class = IngredientTransactionForm
    template_name = "kitchen/ingredienttransaction_form.html"
    success_url = reverse_lazy("kitchen:ingredienttransaction-list")


class IngredientTransactionDeleteView(generic.DeleteView):
    model = IngredientTransaction
    template_name = "kitchen/ingredienttransaction_confirm_delete.html"
    success_url = reverse_lazy("kitchen:ingredienttransaction-list")


class OrderListView(generic.ListView):
    model = Order
    template_name = "kitchen/order_list.html"
    context_object_name = "order_list"
    paginate_by = 5

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items__dish')

        self.form = OrderSearchForm(self.request.GET)

        if self.form.is_valid():
            field = self.form.cleaned_data.get('field') or 'id'
            query = self.form.cleaned_data.get('query', '')

            if field == 'id' and query.isdigit():
                queryset = queryset.filter(id=int(query))
            elif field == 'created_at' and query:
                queryset = queryset.filter(created_at__date=query)

        orders = list(queryset)
        sort_field = self.request.GET.get('sort', 'id')
        sort_dir = self.request.GET.get('dir', 'asc')

        if sort_field == 'total_price':
            orders.sort(key=lambda o:
                        o.total_price,
                        reverse=(sort_dir == 'desc')
                        )
        else:
            allowed_sort_fields = ['id', 'created_at']
            if sort_field in allowed_sort_fields:
                orders.sort(key=lambda o:
                            getattr(o, sort_field),
                            reverse=(sort_dir == 'desc')
                            )

        return orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form
        context['current_sort_field'] = self.request.GET.get('sort', 'id')
        context['current_sort_dir'] = self.request.GET.get('dir', 'asc')
        return context


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

        if items.is_valid():
            out_of_stock = []
            for order_item_form in items:
                dish = order_item_form.cleaned_data.get('dish')
                quty = order_item_form.cleaned_data.get('quantity', 0)
                if dish and quty:
                    for di in dish.dishingredient_set.all():
                        ingredient = di.ingredient
                        if ingredient.stock_amount < di.amount_required * quty:
                            out_of_stock.append(ingredient.name)
            if out_of_stock:
                messages.error(self.request,
                               f"Ingredient(s) out of stock: "
                               f"{', '.join(out_of_stock)}")
                return self.render_to_response(
                    self.get_context_data(form=form)
                )

            with transaction.atomic():
                self.object = form.save()
                items.instance = self.object
                items.save()

                for order_item in self.object.items.all():
                    dish = order_item.dish
                    quty = order_item.quantity
                    for di in dish.dishingredient_set.all():
                        ingredient = di.ingredient
                        ingredient.stock_amount -= di.amount_required * quty
                        ingredient.save()

            return redirect('kitchen:order-list')

        return self.form_invalid(form)


class OrderUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "kitchen/order_form.html"
    success_url = reverse_lazy("kitchen:order-list")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = OrderItemFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            data['items'] = OrderItemFormSet(instance=self.object)
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
                    quty = order_item.quantity
                    for di in dish.dishingredient_set.all():
                        ingredient = di.ingredient
                        ingredient.stock_amount -= di.amount_required * quty
                        if ingredient.stock_amount < 0:
                            ingredient.stock_amount = 0
                        ingredient.save()

        return redirect(self.success_url)


class OrderDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Order
    template_name = "kitchen/order_confirm_delete.html"
    success_url = reverse_lazy("kitchen:order-list")


class IngredientDetailView(generic.DetailView):
    model = Ingredient
    template_name = "kitchen/ingredient_detail.html"
    context_object_name = "ingredient"


class IngredientTransactionDetailView(generic.DetailView):
    model = IngredientTransaction
    template_name = "kitchen/ingredienttransaction_detail.html"
    context_object_name = "transaction"


def finance_dashboard(request):
    fm = FinanceManager()

    print("SUPPLY ON STOCK:", fm.supply_on_stock)

    context = {
        "supply_on_stock": fm.supply_on_stock,
        "supply_cost": fm.supply_cost,
        "revenue": fm.revenue,
        "employee_costs": fm.employee_costs,
        "fixed_costs": fm.fixed_costs,
        "net_profit": fm.net_profit,
        "profit_with_stock": fm.profit_with_stock,
    }
    return render(request, "kitchen/finance_dashboard.html", context)


@login_required
def toggle_assign_to_dish(request, pk):
    chef = Chef.objects.get(id=request.user.id)
    if (
        Dish.objects.get(id=pk) in chef.dishes.all()
    ):
        chef.dishes.remove(pk)
    else:
        chef.dishes.add(pk)
    return HttpResponseRedirect(reverse_lazy("kitchen:dish-detail", args=[pk]))


class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
