import rollbar
from django.core.management.base import BaseCommand
from django.db.models import Q
from witswap.models import WitnetToEthereumSwap
from witswap.node.witnet_node import WitnetNode
import sys
import fcntl


file_handle = None


def file_is_locked(_file_path):
    global file_handle
    file_handle = open(_file_path, 'w')
    try:
        fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False
    except IOError:
        return True


file_path = '/var/lock/test.py'


class Command(BaseCommand):
    def handle(self, *args, **options):
        if file_is_locked(file_path):
            print('another instance is running exiting now')
            return
        
        witnet_node = WitnetNode('localhost', '21338')

        swaps = WitnetToEthereumSwap.objects.filter(Q(status='Waiting For Funds') |
                                                    Q(status='Waiting For User Confirm'))

        for swap in swaps:
            try:
                result = witnet_node.get_balance(swap.receive_user_funds_at.address)
                swap.total_funds_received = result['confirmed']
                swap.unconfirmed_funds_received = result['total'] - result['confirmed']

                if swap.total_funds_received > 0 and swap.status == 'Waiting For Funds':
                    print('Updating status for WitnetToEthereumSwap #%s' % swap.id)
                    swap.status = 'Waiting For User Confirm'

                swap.full_clean()
                swap.save()
            except Exception as e:
                print(e)
                rollbar.report_exc_info(sys.exc_info())
