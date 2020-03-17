from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Item


# Create your views here.

class HomeView(ListView):
    model = Item
    template_name = "core/home.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "core/product.html"


def item_list(request):
    return render(request, "core/home.html", {"items": Item.objects.all})


def checkout_page(request):
    return render(request, "core/checkout.html", {})
