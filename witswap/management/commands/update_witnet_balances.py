import sys
import rollbar
from django.core.management.base import BaseCommand
from django.db.models import Q
from witswap.models import WitnetToEthereumSwap
from witswap.node.witnet_node import WitnetNode


class Command(BaseCommand):
    def handle(self, *args, **options):
        witnet_node = WitnetNode('localhost', '21338')

        swaps = WitnetToEthereumSwap.objects.filter(Q(status='Waiting For Funds') |
                                                    Q(status='Waiting For User Confirm'))

        for swap in swaps:
            try:
                result = witnet_node.get_balance(swap.receive_user_funds_at.address)
                swap.total_funds_received = result[swap.receive_user_funds_at.address]['confirmed']
                swap.unconfirmed_funds_received = result[swap.receive_user_funds_at.address]['total'] - result[swap.receive_user_funds_at.address]['confirmed']

                if swap.total_funds_received > 0 and swap.status == 'Waiting For Funds':
                    print('Updating status for WitnetToEthereumSwap #%s' % swap.id)
                    swap.status = 'Waiting For User Confirm'

                swap.full_clean()
                swap.save()
            except Exception as e:
                print(e)
                rollbar.report_exc_info(sys.exc_info())
