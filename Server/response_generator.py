from database_handler import DatabaseHandler
from encryption_handler import EncryptionHandler

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

SERVER_VERSION = 1


class ResponseGenerator:
    def __init__(self):
        self.client_id = None
        self.encrypted_aes = None
        self.crc = None

    def set_client_id(self, client_id):
        self.client_id = client_id

    def set_encrypted_aes(self, encrypted_aes):
        self.encrypted_aes = encrypted_aes

    def set_crc(self, crc):
        self.crc = crc

    def response(self, response_code, request_parameters):

        payload = str()

        if response_code == REGISTRATION_ACCEPT:
            payload = self.get_registration_accept_payload(request_parameters)

        elif response_code == REGISTRATION_FAIL:
            payload = self.get_registration_fail_payload()

        elif response_code == RSA_KEY_ACCEPT:
            payload = self.get_rsa_key_accept_payload(
                request_parameters)

        elif response_code == FILE_TRANSFER_SUCCESS:
            payload = self.get_file_transfer_success_payload(
                request_parameters)

        elif response_code == CRC_FINISH:
            payload = self.get_crc_finish_payload(request_parameters)

        elif response_code == RECONNECT_ACCEPT:
            payload = self.get_reconnect_accept_payload(
                request_parameters)

        elif response_code == RECONNECT_FAIL:
            payload = self.get_reconnect_fail_payload(request_parameters)

        elif response_code == INVALID_REQUEST:
            payload = self.get_invalid_request_payload()

        else:
            payload = self.get_invalid_request_payload()

        payload_size = len(payload)

        header = f'{SERVER_VERSION}:{response_code}:{payload_size}'

        return f'{header}:{payload}{NULL_CHAR}'

    def get_registration_accept_payload(self, request_parameters):
        return f'{self.client_id}'

    def get_registration_fail_payload(self):
        return f'{REGISTRATION_FAIL}'

    def get_rsa_key_accept_payload(self, request_parameters):
        return f'{self.client_id}:{self.encrypted_aes}'

    def get_file_transfer_success_payload(self, request_parameters):
        file_size = request_parameters[4]
        file_name = request_parameters[5]
        encrypted_file = request_parameters[6]

        return f'{self.client_id}:{file_size}:{file_name}:{self.crc}'

    def get_crc_finish_payload(self, request_parameters):
        return f'{self.client_id}'

    def get_reconnect_accept_payload(self, request_parameters):
        return f'{self.client_id}:{self.encrypted_aes}'

    def get_reconnect_fail_payload(self, request_parameters):
        client_id_to_send = {self.client_id}

        return f'{self.client_id}'

    def get_invalid_request_payload(self):
        return f'Invalid request. Server responded with an error'
