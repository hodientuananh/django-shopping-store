from django.urls import path
from .views import ItemDetailView, add_to_cart, HomeView, remove_from_cart_and_go_to_product, \
    remove_from_cart_and_go_to_summary, OrderSummaryView, \
    remove_one_item_from_cart, add_one_item_to_cart, CheckoutView, PaymentView, RefundFormView

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    path("product/<slug>/", ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('remove-from-cart-and-go-to-product/<slug>/', remove_from_cart_and_go_to_product, name="remove-from-cart-and-go-to-product"),
    path('remove-from-cart-and-go-to-summary/<slug>/', remove_from_cart_and_go_to_summary, name="remove-from-cart-and-go-to-summary"),
    path('remove-one-item-from-cart/<slug>/', remove_one_item_from_cart, name="remove-one-item-from-cart"),
    path('add-one-item-to-cart/<slug>/', add_one_item_to_cart, name="add-one-item-to-cart"),
    path('payment/<payment_option>/', PaymentView.as_view(), name="payment"),
    path('request-refund/', RefundFormView.as_view(), name="request-refund"),
]
