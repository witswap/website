from django.core.management.base import BaseCommand
from witswap.models import Configuration
from witswap.node.witnet_node import WitnetNode


class Command(BaseCommand):
    def handle(self, *args, **options):
        witnet_node = WitnetNode('localhost', '21338', '/home/witnet/logs/', 'witnet-test')
        result = witnet_node.get_sync_status()
        print(result['node_state'])
        configuration = Configuration.objects.all()[0]
        configuration.is_node_synced = result['node_state'] == 'Synced'
        configuration.full_clean()
        configuration.save()
