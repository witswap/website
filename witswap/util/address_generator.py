import hashlib
import ecdsa
from enum import Enum


class Encoding(Enum):
    """Enumeration type to list the various supported encodings."""
    BECH32 = 1
    BECH32M = 2


class AddressGenerator(object):
    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    BECH32M_CONST = 0x2bc830a3

    def __init__(self, hrp):
        self.hrp = hrp

    def bech32_polymod(self, values):
        GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for v in values:
            b = (chk >> 25)
            chk = (chk & 0x1ffffff) << 5 ^ v
            for i in range(5):
                chk ^= GEN[i] if ((b >> i) & 1) else 0
        return chk

    def bech32_hrp_expand(self):
        return [ord(h) >> 5 for h in self.hrp] + [0] + [ord(h) & 31 for h in self.hrp]

    def bech32_create_checksum(self, data):
        values = self.bech32_hrp_expand() + data
        polymod = self.bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
        return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

    def public_key_to_address(self, public_key):
        h1 = hashlib.sha256(bytearray.fromhex(public_key)).digest()[:20]

        h2 = "".join([bin(nibble)[2:].zfill(8) for nibble in h1])
        h3 = [int(h2[i: i + 5], 2) for i in range(0, len(h2), 5)]

        checksum = self.bech32_create_checksum(h3)

        h4 = h3 + checksum

        address = self.hrp + "1" + "".join([self.CHARSET[i] for i in h4])

        return address

    def bech32_decode(self, bech):
        """Validate a Bech32/Bech32m string, and determine HRP and data."""
        if ((any(ord(x) < 33 or ord(x) > 126 for x in bech)) or
                (bech.lower() != bech and bech.upper() != bech)):
            return (None, None, None)
        bech = bech.lower()
        pos = bech.rfind('1')
        if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
            return (None, None, None)
        if not all(x in self.CHARSET for x in bech[pos + 1:]):
            return (None, None, None)
        hrp = bech[:pos]
        data = [self.CHARSET.find(x) for x in bech[pos + 1:]]
        spec = self.bech32_verify_checksum(hrp, data)
        if spec is None:
            return (None, None, None)
        return (hrp, data[:-6], spec)

    def bech32_verify_checksum(self, hrp, data):
        """Verify a checksum given HRP and converted data characters."""
        const = self.bech32_polymod(self.bech32_hrp_expand(hrp) + data)
        if const == 1:
            return Encoding.BECH32
        if const == self.BECH32M_CONST:
            return Encoding.BECH32M
        return None

    def generate_key(self):
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # this is your sign (private key)
        private_key = sk.to_string().hex()  # convert your private key to hex
        vk = sk.get_verifying_key()  # this is your verification key (public key)
        public_key = vk.to_string().hex()

        h1 = hashlib.sha256(bytearray.fromhex(public_key)).digest()[:20]

        h2 = "".join([bin(nibble)[2:].zfill(8) for nibble in h1])
        h3 = [int(h2[i: i + 5], 2) for i in range(0, len(h2), 5)]

        checksum = self.bech32_create_checksum(h3)

        h4 = h3 + checksum

        address = self.hrp + "1" + "".join([self.CHARSET[i] for i in h4])

        return address, private_key, public_key
