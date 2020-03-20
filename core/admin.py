from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, BillingAddress, UserProfile, Refund


# Register your models here.

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


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
    actions = [make_refund_accepted]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(BillingAddress)
admin.site.register(Payment)
admin.site.register(UserProfile)
admin.site.register(Refund)
