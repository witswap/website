# -*- encoding: utf-8 -*-
from django.db.models import Sum
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from witswap.models import WitnetToEthereumSwap, EthereumToWitnetSwap, Configuration
from witswap.settings import EWIT_TOKEN_ADDRESS
from witswap.utils import create_witnet_to_ethereum_swap, validate_ethereum_address, get_fee_from_smart_contract


def balance(request, uuid):
    swaps = WitnetToEthereumSwap.objects.filter(uuid=uuid)
    if not swaps.exists():
        return HttpResponseNotFound()
    swap = swaps[0]

    if swap.status == 'Waiting For User Confirm':
        return JsonResponse({'balance': int(swap.total_funds_received / 1e9),
                             'unconfirmed_balance': int(swap.unconfirmed_funds_received / 1e9)})
    elif swap.status == 'Waiting For Funds':
        return JsonResponse({'balance': 0,
                             'unconfirmed_balance': int(swap.unconfirmed_funds_received / 1e9)})

    return HttpResponseBadRequest(content='Invalid status: ' + swap.status)


def accept(request, uuid):
    if request.method == 'POST':
        swaps = WitnetToEthereumSwap.objects.filter(uuid=uuid)
        if not swaps.exists():
            return HttpResponseNotFound()
        swap = swaps[0]

        minimum_swap_amount = Configuration.objects.all()[0].minimum_swap_amount
        if swap.status == 'Waiting For User Confirm' and swap.total_funds_received >= minimum_swap_amount:
            swap.status = 'Waiting To Be Processed'
            fee_percentage = Configuration.objects.all()[0].fee_percentage
            deduct = 1 - fee_percentage / 100
            swap.total_swapped = int(swap.total_funds_received * deduct)
            swap.full_clean()
            swap.save()

            return JsonResponse({'updated': True})

    return HttpResponseBadRequest()


def create_swap(request, params):
    send_swapped_funds_to = request.POST.get('send_swapped_funds_to')

    if validate_ethereum_address(send_swapped_funds_to):
        address, uuid = create_witnet_to_ethereum_swap(send_swapped_funds_to)
        return render(request, 'templates/index.html', {**params, **{'address': address, 'swap_uuid': uuid}})

    return render(request, 'templates/index.html', {**params, **{'error': 'Invalid address'}})


def get_last_transactions():
    transactions_1 = WitnetToEthereumSwap.objects.filter(status='Finished')
    transactions_2 = EthereumToWitnetSwap.objects.filter(swap_completed=True)

    transactions = []

    for transaction in transactions_1:
        tx_hash = ''
        if transaction.swap_ethereum_transaction_hash:
            tx_hash = transaction.swap_ethereum_transaction_hash[:6] + '...' + transaction.swap_ethereum_transaction_hash[60:]
        link = 'https://rinkeby.etherscan.io/tx/%s' % transaction.swap_ethereum_transaction_hash
        total_funds_received = str(int(transaction.total_funds_received / 1e9))
        total_swapped = str(int(transaction.total_swapped / 1e9))
        transactions.append({'input': total_funds_received + ' WIT',
                             'output': total_swapped + ' eWIT',
                             'date': transaction.date_created,
                             'transaction_hash': tx_hash,
                             'transaction_link': link})

    for transaction in transactions_2:
        tx_hash = ''
        if transaction.swap_witnet_transaction_hash:
            tx_hash = transaction.swap_witnet_transaction_hash[:6] + '...' + transaction.swap_witnet_transaction_hash[58:]
        link = 'https://witnet.network/search/%s' % transaction.swap_witnet_transaction_hash
        initial_amount = str(int(transaction.initial_amount / 1e9))
        swapped_amount = str(int(transaction.swapped_amount / 1e9))
        transactions.append({'input': initial_amount + ' eWIT',
                             'output': swapped_amount + ' WIT',
                             'date': transaction.date_created,
                             'transaction_hash': tx_hash,
                             'transaction_link': link})

    transactions.sort(key=lambda tx: tx['date'], reverse=True)

    return transactions[:20]


def index(request):
    transactions = get_last_transactions()

    total_swapped = WitnetToEthereumSwap.objects.filter(status='Finished').aggregate(Sum('total_funds_received'))
    total_swapped = total_swapped['total_funds_received__sum'] or 0

    fee_percentage = Configuration.objects.all()[0].fee_percentage
    minimum_burn_amount = Configuration.objects.all()[0].minimum_burn_amount

    params = {'address': None,
              'minimum_burn_amount': minimum_burn_amount,
              'fee_percentage': fee_percentage,
              'transactions': transactions,
              'token_address': EWIT_TOKEN_ADDRESS,
              'total_swapped': int(total_swapped / 1e9)}

    if request.method == 'POST':
        return create_swap(request, params)

    return render(request, 'templates/index.html', params)


def handler500(request):
    return render(request, 'templates/error.html', {})
