from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY


def get_fernet():
    if not ENCRYPTION_KEY:
        key = Fernet.generate_key()
        print(f"WARNING: No ENCRYPTION_KEY set. Generated temporary key: {key.decode()}")
        print("Set this in your .env file for persistence.")
        return Fernet(key)
    return Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


_fernet = None


def fernet():
    global _fernet
    if _fernet is None:
        _fernet = get_fernet()
    return _fernet


def encrypt_value(plaintext: str) -> bytes:
    return fernet().encrypt(plaintext.encode())


def decrypt_value(ciphertext: bytes) -> str:
    return fernet().decrypt(ciphertext).decode()
