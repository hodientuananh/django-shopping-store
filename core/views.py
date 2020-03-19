from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CheckoutForm, PaymentForm
from .models import Item, Order, OrderItem, BillingAddress, Payment, UserProfile

import stripe

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"


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
                bill_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                bill_address.save()
                order.billing_address = bill_address
                order.save()

                if payment_option == "S":
                    return redirect("core:payment", payment_option="stripe")
                else:
                    messages.warning(self.request, "PayPal is not available now")
                    return redirect("core:checkout")
            messages.warning(self.request, "Form is invalid")
            return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have active order")
            return redirect("/")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                "order": order
            }
            return render(self.request, "core/payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')
            amount = int(order.get_final_price() * 100)

            try:
                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.user = self.request.user
                payment.stripe_charge_id = charge['id']
                payment.amount = order.get_final_price()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("core:payment/stripe")


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
