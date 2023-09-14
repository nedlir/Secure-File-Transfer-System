import base64
import binascii
import os
import zlib

try:
    from Crypto.Random import get_random_bytes
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
except ImportError as e:
    print(e)
    print('Package not found. Install required packages from requirements.txt file')
    exit()

from database_handler import DatabaseHandler


class EncryptionHandler:

    def __init__(self):
        self.database_handler = DatabaseHandler()
        self.AES_key = None
        self.public_RSA_key = None

    def generate_AES_key(self, client_name):
        self.AES_key = base64.b64encode(
            get_random_bytes(16))  # 16 bytes of random bytes
        self.database_handler.update_AES_key(client_name, self.AES_key)

    def get_encrypted_AES_key(self, client_name):
        self.public_RSA_key = self.database_handler.get_public_RSA_key(
            client_name)
        # Convert the base64-encoded public key string to an RSA public key object
        decoded_rsa = RSA.import_key(base64.b64decode(self.public_RSA_key))
        # Use PKCS1_OAEP padding scheme to encrypt the AES key with the RSA public key
        cipher_rsa = PKCS1_OAEP.new(decoded_rsa)
        encrypted_AES_key = cipher_rsa.encrypt(self.AES_key)
        # Encode the encrypted AES key in base64 for transport
        return base64.b64encode(encrypted_AES_key).decode()

    def decrypt_file(self, encrypted_data, aes_key, file_name):

        AES_IV_SIZE = 16

        key = base64.b64decode(aes_key)
        iv = encrypted_data[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        padded_plaintext = cipher.decrypt(encrypted_data[AES.block_size:])
        plaintext = unpad(padded_plaintext, AES_IV_SIZE)

        return plaintext

    def calculate_crc(self, client_name, file_name):
        chunk = 1024
        crc_value = 0
        file_path = os.path.join(client_name, file_name)
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(chunk)
                if not data:
                    break
                crc_value = zlib.crc32(data, crc_value)

        # Verify crc_value doesn't exceed 4 bytes
        crc_bytes = crc_value.to_bytes(4, byteorder='big', signed=False)
        if len(crc_bytes) > 4:
            raise ValueError("CRC value exceeds 4 bytes")

        return crc_value
