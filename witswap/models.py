from django.db import models
from django.utils import timezone
import uuid


class Custodian(models.Model):
    description = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.description

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Custodian"
        verbose_name_plural = "Custodians"


class WitnetAddress(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    address = models.CharField(max_length=42, unique=True)
    custodian = models.ForeignKey(Custodian, null=True, blank=True, on_delete=models.SET_NULL)

    def was_used(self):
        return WitnetToEthereumSwap.objects.filter(receive_user_funds_at=self).exists()
    was_used.boolean = True

    def __unicode__(self):
        return self.address

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = "Witnet Address"
        verbose_name_plural = "Witnet Addresses"


STATUSES = (
    ('Waiting For Funds', 'Waiting For Funds'),
    ('Waiting For User Confirm', 'Waiting For User Confirm'),
    ('Waiting To Be Processed', 'Waiting To Be Processed'),
    ('Finished', 'Finished'),
    ('Bounced', 'Bounced'),
)


class WitnetToEthereumSwap(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    send_swapped_funds_to = models.CharField(max_length=42)
    receive_user_funds_at = models.ForeignKey(WitnetAddress, on_delete=models.CASCADE, related_name='swap')
    total_funds_received = models.BigIntegerField(default=0)
    unconfirmed_funds_received = models.BigIntegerField(default=0)
    total_swapped = models.BigIntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUSES, default='Waiting For Funds')
    swap_ethereum_transaction_hash = models.CharField(max_length=66, null=True, blank=True, unique=True)
    uuid = models.UUIDField(default=uuid.uuid4)

    class Meta:
        verbose_name = "Witnet To Ethereum Swap"
        verbose_name_plural = "Witnet To Ethereum Swaps"


class EthereumToWitnetSwap(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    initial_amount = models.BigIntegerField()
    swapped_amount = models.BigIntegerField()
    send_converted_funds_to = models.CharField(max_length=42)
    burn_ethereum_transaction_hash = models.CharField(max_length=66, null=True, blank=True, unique=True)
    swap_completed = models.BooleanField(default=False)
    swap_witnet_transaction_hash = models.CharField(max_length=64, null=True, blank=True, unique=True)
    custodian = models.ForeignKey(Custodian, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Ethereum To Witnet Swap"
        verbose_name_plural = "Ethereum To Witnet Swaps"


class Configuration(models.Model):
    ethereum_events_from_block = models.IntegerField(default=0)
    last_custodian_assigned = models.ForeignKey(Custodian, null=True, blank=True, on_delete=models.SET_NULL)
    is_node_synced = models.BooleanField(default=True)
    fee_percentage = models.IntegerField(default=5)
    minimum_swap_amount = models.BigIntegerField(default=10000000000000, help_text='Remember to add the 9 decimals')

    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"
