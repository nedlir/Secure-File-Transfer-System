import base64
import os
import re

from verification import is_valid_client_id, is_valid_client_name

try:
    from Crypto.Cipher import AES
except ImportError as e:
    print(e)
    print('Package not found. Install required packages from requirements.txt file')
    exit()

from files_handler import FilesHandler
from response_generator import ResponseGenerator

# Responses
NULL_CHAR = '\0'
REGISTRATION_ACCEPT = 2100
REGISTRATION_FAIL = 2101
RSA_KEY_ACCEPT = 2102
FILE_TRANSFER_SUCCESS = 2103
CRC_FINISH = 2104
RECONNECT_ACCEPT = 2105
RECONNECT_FAIL = 2106
INVALID_REQUEST = 2107

# Requests
REGISTRATION_REQUEST = 1100
KEYS_EXCHANGE_REQUEST = 1101
RECONNECT_REQUEST = 1102
FILE_TRANSFER_REQUEST = 1103
VALID_CKSUM_FINISH_REQUEST = 1104
INVALID_CKSUM_RESEND_REQUEST = 1105
INVALID_CKSUM_FINISH_REQUEST = 1106


class NetworkHandler:
    def __init__(self, database_handler, encryption_handler):
        self.database_handler = database_handler
        self.encryption_handler = encryption_handler
        self.files_handler = FilesHandler()
        self.response_generator = ResponseGenerator()
        self.client_id = str()
        self.client_name = str()

    def parse_request(self, request: bytes):
        decoded_request = request.decode()
        request_parameters = decoded_request.split(":")
        request_code = request_parameters[2]
        return int(request_code), request_parameters

    def handle_registration_request(self, request_parameters):

        self.client_name = request_parameters[4]
        if not is_valid_client_name(self.client_name):
            return self.response_generator.response(INVALID_REQUEST, request_parameters)

        if self.database_handler.is_client_exists(self.client_name):
            return self.response_generator.response(REGISTRATION_FAIL, request_parameters)

        self.database_handler.register_client(self.client_name)

        self.client_id = self.database_handler.get_client_id(self.client_name)

        client_id = self.database_handler.get_client_id(
            self.client_name)

        self.response_generator.set_client_id(self.client_id.hex())
        return self.response_generator.response(REGISTRATION_ACCEPT, request_parameters)

    def handle_reconnect_request(self, request_parameters):
        self.client_id = request_parameters[0]
        self.client_name = request_parameters[4]
        if (not is_valid_client_id(self.client_id) or not is_valid_client_name(self.client_name)):
            return self.response_generator.response(INVALID_REQUEST, request_parameters)

        if not self.database_handler.is_RSA_key_exists(self.client_name):
            # RSA key or client don't exist, reconnection failed response
            self.response_generator.set_client_id(self.client_id)
            return self.response_generator.response(RECONNECT_FAIL, request_parameters)

        # Generate a new AES key, save it to database and encrypt it with the client's public key
        self.encryption_handler.generate_AES_key(self.client_name)
        encrypted_aes = self.encryption_handler.get_encrypted_AES_key(
            self.client_name)

        self.database_handler.update_last_seen(self.client_id)

        self.response_generator.set_client_id(self.client_id)
        self.response_generator.set_encrypted_aes(encrypted_aes)
        return self.response_generator.response(RECONNECT_ACCEPT, request_parameters)

    def handle_key_exchange_request(self, request_parameters):
        public_key = request_parameters[5]
        self.database_handler.update_public_RSA_key(
            self.client_name, public_key)

        # Generate a new AES key, save it to database and encrypt it with the client's public key
        self.encryption_handler.generate_AES_key(self.client_name)
        encrypted_aes = self.encryption_handler.get_encrypted_AES_key(
            self.client_name)

        self.database_handler.update_last_seen(self.client_id)

        self.response_generator.set_encrypted_aes(encrypted_aes)
        return self.response_generator.response(RSA_KEY_ACCEPT, request_parameters)

    def handle_file_transfer_request(self, request_parameters):
        # Unpack relevant variables
        file_size = request_parameters[4]
        file_name = request_parameters[5]
        encrypted_file = request_parameters[6]

        # Save file
        aes_key = self.database_handler.get_AES_key(self.client_name)

        encrypted_file = base64.b64decode(encrypted_file)

        decrypted_file_content = self.encryption_handler.decrypt_file(
            encrypted_file, aes_key, file_name)
        self.files_handler.save_decrypted_file(
            self.client_name, file_name, decrypted_file_content)

        # Update database with file info
        self.database_handler.update_file_info(
            self.client_id, self.client_name, file_name)
        self.database_handler.update_crc(self.client_id, False)

        crc = self.encryption_handler.calculate_crc(
            self.client_name, file_name)

        self.database_handler.update_last_seen(self.client_id)

        self.response_generator.set_crc(crc)
        return self.response_generator.response(FILE_TRANSFER_SUCCESS, request_parameters)

    def handle_cksum_finish_request(self, request_parameters, request_code):
        # is successful CRC? yes or no
        crc_request = bool()
        if request_code == VALID_CKSUM_FINISH_REQUEST:
            crc_request = True
        elif request_code == INVALID_CKSUM_FINISH_REQUEST:
            crc_request = False

        self.database_handler.update_crc(self.client_id, crc_request)

        self.database_handler.update_last_seen(self.client_id)

        return self.response_generator.response(CRC_FINISH, request_parameters)

    def handle_invalid_cksum_request(self, request_parameters):
        self.database_handler.update_crc(self.client_id, False)
        # request 1103 (FILE_TRANSFER_REQUEST) is about to be resent

    def handle_unknown_request(self, request_parameters):
        self.database_handler.update_last_seen(self.client_id)

        return self.response_generator.response(INVALID_REQUEST, request_parameters)
