from django.urls import path
from .views import item_list, checkout_page, ItemDetailView

app_name = 'core'
urlpatterns = [
    path("", item_list, name="item-list"),
    path("checkout", checkout_page, name="checkout"),
    path("product/<slug>/", ItemDetailView.as_view(), name="product")
]
