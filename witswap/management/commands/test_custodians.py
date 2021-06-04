from django.core.management.base import BaseCommand

from witswap.utils import get_custodian_with_round_robin, get_fee_from_smart_contract


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(get_custodian_with_round_robin().description)
        print(get_custodian_with_round_robin().description)
        print(get_custodian_with_round_robin().description)
        print(get_custodian_with_round_robin().description)
