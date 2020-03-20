from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, BillingAddress, UserProfile

# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'billing_address',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    ]
    list_display_links = [
        'user',
        'billing_address',
    ]
    list_filter = ['user',
                   'ordered',
                   'billing_address',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted',
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(BillingAddress)
admin.site.register(Payment)
admin.site.register(UserProfile)
