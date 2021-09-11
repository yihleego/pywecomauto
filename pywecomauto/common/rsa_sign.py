# -*- coding: utf-8 -*-
import base64

from Crypto.Hash import SHA1
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


def generate(key_size=2048, pkcs=1):
    key_pair = RSA.generate(key_size)
    private_key = key_pair.export_key(format='DER', pkcs=pkcs)
    public_key = key_pair.public_key().export_key(format='DER', pkcs=pkcs)
    return private_key, public_key


def generate_base64(key_size=2048, pkcs=1):
    key_pair = generate(key_size, pkcs)
    return to_base64(key_pair[0]), to_base64(key_pair[1])


def sign_sha256(private_key: str, data: str):
    return _sign_base64(private_key, data, SHA256)


def verify_sha256(public_key: str, data: str, signature: str):
    return _verify_base64(public_key, data, signature, SHA256)


def sign_sha1(private_key: str, data: str):
    return _sign_base64(private_key, data, SHA1)


def verify_sha1(public_key: str, data: str, signature: str):
    return _verify_base64(public_key, data, signature, SHA1)


def _sign_base64(private_key: str, data: str, algorithm):
    signature = _sign_bytes(base64.b64decode(private_key), to_bytes(data), algorithm)
    return to_base64(signature)


def _verify_base64(public_key: str, data: str, signature: str, algorithm):
    return _verify_bytes(base64.b64decode(public_key), to_bytes(data), base64.b64decode(signature), algorithm)


def _sign_bytes(private_key: bytes, data: bytes, algorithm):
    digest = algorithm.new(data)
    key = RSA.import_key(private_key)
    return pkcs1_15.new(key).sign(digest)


def _verify_bytes(public_key: bytes, data: bytes, signature: bytes, algorithm):
    try:
        digest = algorithm.new(data)
        key = RSA.import_key(public_key)
        pkcs1_15.new(key).verify(digest, signature)
        return True
    except (ValueError, TypeError):
        return False


def to_bytes(data: str):
    return bytes(data, encoding="utf8")


def to_base64(buffer: bytes):
    return str(base64.b64encode(buffer), encoding="utf-8")


if __name__ == '__main__':
    k = generate(pkcs=1)
    print(to_base64(k[0]))
    print(to_base64(k[1]))
    signature = _sign_bytes(k[0], b'123456', SHA256)
    result = _verify_bytes(k[1], b'123456', signature, SHA256)
    print(to_base64(signature))
    print(result)
    pass
