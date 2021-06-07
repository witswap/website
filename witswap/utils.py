from bitcoinaddress.segwit_addr import bech32_verify_checksum
from web3 import Web3, HTTPProvider

from witswap.models import WitnetAddress, WitnetToEthereumSwap, EthereumToWitnetSwap, Configuration, Custodian
from django.db.models import Q


# def generate_witnet_address():
#     address_generator = AddressGenerator("wit")
#     address, public_key, private_key = address_generator.generate_key()
#
#     witnet_address = WitnetAddress()
#     witnet_address.address = address
#     witnet_address.encrypted_private_key = private_key
#     witnet_address.full_clean()
#     witnet_address.save()
#
#     return witnet_address


# def generate_ethereum_address():
#     timestamp = str(datetime.datetime.now().timestamp())
#     account = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ %s' % timestamp)
#     public_key = account.address
#     private_key = str(account.privateKey.hex()).replace('0x', '')
#
#     ethereum_address = EthereumAddress()
#     ethereum_address.address = public_key
#     ethereum_address.encrypted_private_key = private_key
#     ethereum_address.full_clean()
#     ethereum_address.save()
#
#     return ethereum_address
from witswap.settings import INFURA_URL, EWIT_TOKEN_ADDRESS


def get_unused_witnet_address():
    custodian = get_custodian_with_round_robin()
    return WitnetAddress.objects.filter(swap=None, custodian=custodian)[0]


def create_witnet_to_ethereum_swap(send_swapped_funds_to):
    swaps = WitnetToEthereumSwap.objects.filter(Q(status='Waiting For Funds') |
                                                Q(status='Waiting For User Confirm'),
                                                send_swapped_funds_to=send_swapped_funds_to)
    if swaps.exists():
        return swaps[0].receive_user_funds_at.address, swaps[0].uuid

    swap = WitnetToEthereumSwap()
    swap.send_swapped_funds_to = send_swapped_funds_to
    swap.receive_user_funds_at = get_unused_witnet_address()
    swap.full_clean()
    swap.save()

    return swap.receive_user_funds_at.address, swap.uuid


def create_ethereum_to_witnet_swap(send_converted_funds_to, initial_amount,
                                   receive_user_funds_in, transaction_hash):

    swap = EthereumToWitnetSwap()
    swap.initial_amount = initial_amount
    swap.swapped_amount = initial_amount
    swap.send_converted_funds_to = send_converted_funds_to
    swap.receive_user_funds_in = receive_user_funds_in
    swap.burn_ethereum_transaction_hash = transaction_hash
    swap.custodian = get_custodian_with_round_robin()
    swap.full_clean()
    swap.save()


def get_custodian_with_round_robin():
    custodians = Custodian.objects.filter(active=True)

    if len(custodians) == 0:
        return None

    configurations = Configuration.objects.all()
    if len(configurations) == 0:
        config = Configuration()
        config.last_custodian_assigned = custodians[0]
        config.full_clean()
        config.save()
        return custodians[0]

    config = configurations[0]

    assign_next = False
    for custodian in custodians:
        if assign_next:
            config.last_custodian_assigned = custodian
            config.full_clean()
            config.save()
            return custodian
        if custodian == config.last_custodian_assigned:
            assign_next = True
    config.last_custodian_assigned = custodians[0]
    config.full_clean()
    config.save()
    return custodians[0]


def validate_ethereum_address(address):
    return Web3.isAddress(address)


def validate_witnet_address(bech):
    charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
            (bech.lower() != bech and bech.upper() != bech)):
        return False
    bech = bech.lower()
    pos = bech.rfind('1')
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
        return False
    if not all(x in charset for x in bech[pos+1:]):
        return False
    hrp = bech[:pos]
    data = [charset.find(x) for x in bech[pos+1:]]
    if not bech32_verify_checksum(hrp, data):
        return False
    return True


def get_fee_from_smart_contract():
    w3 = Web3(HTTPProvider(INFURA_URL))
    contract = w3.eth.contract(EWIT_TOKEN_ADDRESS, abi=ABI)
    fee = contract.functions.feePercentage().call()
    return fee / 10

ABI = '[{"inputs":[{"internalType":"address","name":"_multisig","type":"address"},{"internalType":"address","name":"_platform","type":"address"},{"internalType":"address","name":"_developer","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"address","name":"etherAddress","type":"address"},{"indexed":false,"internalType":"uint256","name":"total","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"totalMinusFees","type":"uint256"},{"indexed":false,"internalType":"string","name":"witnetFundsReceivedAt","type":"string"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"previousAdminRole","type":"bytes32"},{"indexed":true,"internalType":"bytes32","name":"newAdminRole","type":"bytes32"}],"name":"RoleAdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleGranted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"role","type":"bytes32"},{"indexed":true,"internalType":"address","name":"account","type":"address"},{"indexed":true,"internalType":"address","name":"sender","type":"address"}],"name":"RoleRevoked","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"string","name":"witAddress","type":"string"},{"indexed":false,"internalType":"uint256","name":"total","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"totalMinusFees","type":"uint256"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[],"name":"DEFAULT_ADMIN_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MINTER_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"PAUSER_ROLE","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"developer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"feePercentage","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleAdmin","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"getRoleMember","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"}],"name":"getRoleMemberCount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"grantRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"hasRole","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"minimumSwap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_etherAddress","type":"address"},{"internalType":"uint256","name":"_total","type":"uint256"},{"internalType":"string","name":"_witnetFundsReceivedAt","type":"string"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"platform","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_allowedToMint","type":"uint256"}],"name":"renewMintRound","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"renounceRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"role","type":"bytes32"},{"internalType":"address","name":"account","type":"address"}],"name":"revokeRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"_witAddress","type":"string"},{"internalType":"uint256","name":"_total","type":"uint256"}],"name":"swap","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSwapped","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint8","name":"_newFees","type":"uint8"}],"name":"updateFees","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_newMinimum","type":"uint256"}],"name":"updateMinimum","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

# def validate_witnet_address(address):
#     return address.startswith('wit1') and len(address) == 42
