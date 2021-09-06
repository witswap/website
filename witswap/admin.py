from django.contrib import admin
from django.utils.safestring import mark_safe

from witswap.models import WitnetAddress, WitnetToEthereumSwap, EthereumToWitnetSwap, Configuration, Custodian


class WitnetToEthereumSwapAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', '_custodian', 'date_created', 'send_swapped_funds_to', 'receive_user_funds_at',
                    'total_funds_received', 'unconfirmed_funds_received', 'total_swapped',
                    'swap_ethereum_transaction_hash')
    list_filter = ['status', 'receive_user_funds_at__custodian']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["send_swapped_funds_to", "receive_user_funds_at", 'total_funds_received',
                    'unconfirmed_funds_received', 'date_created']
        else:
            return []

    def _custodian(self, obj):
        return mark_safe(obj.receive_user_funds_at.custodian.description)


admin.site.register(WitnetToEthereumSwap, WitnetToEthereumSwapAdmin)


class EthereumToWitnetSwapAdmin(admin.ModelAdmin):
    list_display = ('id', 'swap_completed', 'custodian', 'date_created', 'initial_amount', 'swapped_amount',
                    'send_converted_funds_to',
                    'burn_ethereum_transaction_hash', 'swap_witnet_transaction_hash')
    list_filter = ['swap_completed', 'custodian']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["burn_ethereum_transaction_hash", "initial_amount", 'swapped_amount',
                    'send_converted_funds_to', 'date_created']
        else:
            return []


admin.site.register(EthereumToWitnetSwap, EthereumToWitnetSwapAdmin)


class WitnetAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_created', 'address', 'was_used')


admin.site.register(WitnetAddress, WitnetAddressAdmin)


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'ethereum_events_from_block', 'last_custodian_assigned', 'is_node_synced',
                    'fee_percentage', 'minimum_swap_amount')


admin.site.register(Configuration, ConfigurationAdmin)


class CustodianAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'active')


admin.site.register(Custodian, CustodianAdmin)
