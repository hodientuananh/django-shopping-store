from django.urls import path
from .views import checkout_page, ItemDetailView, add_to_cart, HomeView

app_name = 'core'
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("checkout", checkout_page, name="checkout"),
    path("product/<slug>/", ItemDetailView.as_view(), name="product"),
    path('add_to_cart/<slug>/', add_to_cart, name="add-to-cart")
]
