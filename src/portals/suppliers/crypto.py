try:
    import urandom
    import ubinascii

    def uuid():
        random_bytes = bytearray(16)
        for i in range(16):
            random_bytes[i] = urandom.getrandbits(8)

        # Set version and variant bits:
        random_bytes[6] = (random_bytes[6] & 0x0F) | 0x40  # Version 4
        random_bytes[8] = (random_bytes[8] & 0x3F) | 0x80  # Variant 1

        hex_str = ubinascii.hexlify(random_bytes).decode()
        return "-".join(
            [hex_str[:8], hex_str[8:12], hex_str[12:16], hex_str[16:20], hex_str[20:]]
        )

except ImportError:
    from uuid import uuid4

    uuid = uuid4


def random_uuid():
    return str(uuid())


crypto = {"random_uuid": random_uuid}


def crypto_supplier(data, scope):
    return crypto
