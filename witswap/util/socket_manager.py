import json
import socket
import struct


class SocketManager(object):
    def __init__(self, ip, port, internal):
        self.ip = ip
        self.port = int(port)
        self.internal = internal

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set socket options
        # Allows close and immediate reuse of an address, ignoring TIME_WAIT
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Always and immediately close a socket, ignoring pending data
        so_onoff, so_linger = 1, 0
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', so_onoff, so_linger))

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def disconnect(self):
        self.socket.close()

    def fetch(self, request):
        self.socket.send((json.dumps(request) + "\n").encode("utf-8"))
        response = ""
        while True:
            response += self.socket.recv(1024).decode("utf-8")
            if len(response) == 0 or response[-1] == "\n":
                break
        if response != "":
            try:
                return json.loads(response)
            except json.decoder.JSONDecodeError:
                print(request, response)
                return {"error": {"code": -1337, "message": "malformed response"}}
        else:
            return {"error": {"code": -1337, "message": "response was empty"}}

    def query(self, request, require_synced=True):
        # If we control the begin- and endpoint of the socket, we can add metadata
        if self.internal:
            request_synced = {"request": request, "require_synced": require_synced}
        else:
            request_synced = request
        response = self.fetch(request_synced)

        reason = "unknown"
        if type(response) is dict and "error" in response:
            reason = response["error"]
            if "reason" in response:
                reason = response["reason"]
            if "params" in request:
                return {"error": "could not execute " + request["method"] + " with parameters " + str(request["params"]), "reason": reason}
            else:
                return {"error": "could not execute " + request["method"], "reason": reason}

        if type(response) is dict and "result" in response:
            return response["result"]
        else:
            return response

    def close_connection(self):
        self.socket.send(b"\n")
        self.disconnect()
