from time import strftime

from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField

# Create your models here.

CATEGORY_CHOICES = (
    ('TS', 'T-Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'Out Wear')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(default=0)
    promote_image = models.CharField(max_length=200)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=100)
    label = models.CharField(choices=LABEL_CHOICES, max_length=100)
    description = models.TextField()
    slug = models.SlugField()

    def __str__(self):
        return self.title

    def hasDiscount(self):
        return 0 <= self.discount_price < self.price

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            "slug": self.slug
        })

    def get_add_to_cart(self):
        return reverse("core:add-to-cart", kwargs={
            "slug": self.slug
        })

    def get_remove_from_cart_and_go_to_product(self):
        return reverse("core:remove-from-cart-and-go-to-product", kwargs={
            "slug": self.slug
        })

    def get_remove_from_cart_and_go_to_summary(self):
        return reverse("core:remove-from-cart-and-go-to-summary", kwargs={
            "slug": self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_total_saved_price(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_total_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        else:
            return self.get_total_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    ref_code = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username + "-" + self.ordered_date.strftime("%m/%d/%Y, %H:%M:%S")

    def get_final_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_final_total_price()
        return total

    def get_final_total_saved_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_total_saved_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=200)
    apartment_address = models.CharField(max_length=200)
    country = CountryField(multiple=True)
    zip = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + "-" + self.timestamp.strftime("%m/%d/%Y, %H:%M:%S")


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
