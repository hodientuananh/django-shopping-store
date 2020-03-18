from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages

from .models import Item, Order, OrderItem


# Create your views here.

class HomeView(ListView):
    model = Item
    template_name = "core/home.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "core/product.html"


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
            order.items.add(order_item)
    else:
        messages.success(request, "Order is added")
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
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
    return redirect("core:product", slug=slug)


def item_list(request):
    return render(request, "core/home.html", {"items": Item.objects.all})


def checkout_page(request):
    return render(request, "core/checkout.html", {})
