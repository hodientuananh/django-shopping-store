from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CheckoutForm
from .models import Item, Order, OrderItem, BillingAdress


class HomeView(ListView):
    model = Item
    paginate_by = 4
    template_name = "core/home.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "core/product.html"


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            "form": form
        }
        return render(self.request, "core/checkout.html", context)

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm(self.request.POST or None)
            if form.is_valid():
                street_address = form.cleaned_data.get("street_address")
                apartment_address = form.cleaned_data.get("apartment_address")
                country = form.cleaned_data.get("country")
                zip = form.cleaned_data.get("zip")
                # same_billing_address = form.cleaned_data.get("same_billing_address")
                # save_info = form.cleaned_data.get("save_info")
                payment_option = form.cleaned_data.get("payment_option")
                bill_address = BillingAdress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                bill_address.save()
                order.billing_address = bill_address
                order.save()
                return redirect("core:checkout")
            messages.warning(self.request, "Form is invalid")
            return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have active order")
            return redirect("/")


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "core/payment.html")

class OrderSummaryView(LoginRequiredMixin, View):
    # model = Order
    # template_name = "core/order_summary.html"
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                "object": order
            }
            return render(self.request, "core/order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have active order")
            return redirect("/")


def remove_all_items_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        if order.items.filter(item__slug=item.slug).exists():
            messages.info(request, "Order is removed")
            OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0].delete()
        else:
            messages.info(request, "No order item can be removed now")
    else:
        messages.info(request, "No order can be removed now")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created_date = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        if order.items.filter(item__slug=item.slug).exists():
            messages.success(request, "Order item is increased to %s" % (order_item.quantity + 1))
            order_item.quantity += 1
            order_item.save()
        else:
            messages.success(request, "Order item is added")
            order_item.quantity = 1
            order.items.add(order_item)
    else:
        messages.success(request, "Order is added")
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect("core:product", slug=slug)


@login_required
def remove_from_cart_and_go_to_product(request, slug):
    remove_all_items_from_cart(request, slug)
    return redirect("core:product", slug=slug)


@login_required
def remove_from_cart_and_go_to_summary(request, slug):
    remove_all_items_from_cart(request, slug)
    return redirect("core:order-summary")


@login_required
def remove_one_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        if order.items.filter(item__slug=item.slug).exists():
            messages.info(request, "Order quantity is decreased 1")
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            return redirect("core:order-summary")
        else:
            messages.info(request, "No order item can be removed now")
    else:
        messages.info(request, "No order can be removed now")
    return redirect("core:product", slug=slug)


@login_required
def add_one_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created_date = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_query_set = Order.objects.filter(user=request.user, ordered=False)
    if order_query_set.exists():
        order = order_query_set[0]
        if order.items.filter(item__slug=item.slug).exists():
            messages.success(request, "Order item is increased to %s" % (order_item.quantity + 1))
            order_item.quantity += 1
            order_item.save()
            return redirect("core:order-summary")
        else:
            messages.success(request, "Order item is added")
            order.items.add(order_item)
    else:
        messages.success(request, "Order is added")
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect("core:product")
