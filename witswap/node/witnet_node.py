#!/usr/bin/python3

import os
from witswap.util.log import Log
from witswap.util.socket_manager import SocketManager


class WitnetNode(object):
    def __init__(self, socket_host, socket_port, path=None, suffix=None):
        if path != None and suffix != None:
            if not os.path.exists(os.path.join(path)):
                os.makedirs(os.path.join(path))

            log_file_name = os.path.join(path, "witnet-" + str(suffix) + ".log")
            self.log = Log(log_file_name, None, "method,response", "method")
        else:
            self.log = None

        self.socket_mngr = SocketManager(socket_host, socket_port, False)
        self.socket_mngr.connect()

    def close_connection(self):
        self.socket_mngr.close_connection()

    #################
    # RPC functions #
    #################

    def get_consensus_constants(self):
        if self.log:
            self.log.log_info("get_consensus_constants()", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getConsensusConstants", "id": "1"}
        return self.execute_request(request, require_synced=False)

    def get_block(self, block_hash):
        if self.log:
            self.log.log_info("get_block("+ str(block_hash) + ")", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getBlock", "params": [block_hash], "id": "1"}
        return self.execute_request(request)

    # Return a <num_blocks> hashes, starting at <epoch>
    # <num_blocks>: default is 0 (returning all blocks), a negative value returns the hashes for the last x epochs
    # <epoch>: default is 0 (start at epoch 0), a negative value returns the hashes for the last x epochs
    # Note that one should combine a positive <epoch> with a positive <num_blocks>
    def get_blockchain(self, epoch=0, num_blocks=0):
        if self.log:
            self.log.log_info("get_blockchain("+ str(epoch) + ", " + str(num_blocks) + ")", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getBlockChain", "params": [epoch, num_blocks], "id": "1"}
        return self.execute_request(request)

    def get_address(self):
        if self.log:
            self.log.log_info("get_address()", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getPkh", "id": "1"}
        return self.execute_request(request, require_synced=False)

    def get_balance(self, node_addresses):
        if self.log:
            self.log.log_info("get_balance(" + ",".join(node_addresses) + ")", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getBalance", "params": [node_addresses], "id": "1"}
        return self.execute_request(request)

    def get_reputation(self, node_address):
        if self.log:
            self.log.log_info("get_reputation(" + node_address + ")", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getReputation", "params": [node_address], "id": "1"}
        return self.execute_request(request)

    def get_reputation_all(self):
        if self.log:
            self.log.log_info("get_reputation_all()", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getReputationAll", "id": "1"}
        return self.execute_request(request)

    def get_transaction(self, txn_hash):
        if self.log:
            self.log.log_info("get_transaction(" + str(txn_hash) + ")", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getTransaction", "params": [txn_hash], "id": "1"}
        return self.execute_request(request)

    def get_sync_status(self):
        if self.log:
            self.log.log_info("get_sync_status()", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "syncStatus", "id": "1"}
        return self.execute_request(request)

    def get_known_peers(self):
        if self.log:
            self.log.log_info("get_known_peers()", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "knownPeers", "id": "1"}
        return self.execute_request(request)

    def get_mempool(self):
        if self.log:
            self.log.log_info("get_mempool()", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getMempool", "id": "1"}
        return self.execute_request(request)

    def get_current_epoch(self):
        if self.log:
            self.log.log_info("get_current_epoch()", prefix="node", message_type="method")
        blockchain = self.get_blockchain(-1, -1)
        return blockchain[0][0]

    def get_supply_info(self):
        if self.log:
            self.log.log_info("get_supply_info()", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getSupplyInfo", "id": "1"}
        return self.execute_request(request)

    def get_utxos(self, address):
        if self.log:
            self.log.log_info("get_utxos(" + str(address) + ")", prefix="node", message_type="method")
        request = {"jsonrpc": "2.0", "method": "getUtxoInfo", "params": [address], "id": "1"}
        return self.execute_request(request)

    def execute_request(self, request, require_synced=True):
        response = self.socket_mngr.query(request, require_synced=require_synced)
        if self.log:
            self.log.log_info("Result for " + str(request) + ": " + str(response), prefix="node", message_type="response")
        print(str(response))
        return response
