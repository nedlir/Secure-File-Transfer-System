from database_handler import DatabaseHandler
from encryption_handler import EncryptionHandler
from network_handler import NetworkHandler
from verification import is_valid_request_code


RECEIVE_BUFFER_SIZE = 1024

# Requests
REGISTRATION_REQUEST = 1100
KEYS_EXCHANGE_REQUEST = 1101
RECONNECT_REQUEST = 1102
FILE_TRANSFER_REQUEST = 1103
VALID_CKSUM_FINISH_REQUEST = 1104
INVALID_CKSUM_RESEND_REQUEST = 1105
INVALID_CKSUM_FINISH_REQUEST = 1106


class Protocol:
    def handle_client_requests(client_connect, client_address):
        database_handler = DatabaseHandler()
        encryption_handler = EncryptionHandler()
        network_handler = NetworkHandler(
            database_handler, encryption_handler)

        print(f"[INFO] New connection from {client_address}")

        while True:  # receive requests from client
            # Receive the request from the client

            try:
                request = client_connect.recv(RECEIVE_BUFFER_SIZE)

                print(f'REQUEST RECEIVED: {request.decode()}')

                if not request:
                    print(f"[INFO] Connection closed by {client_address}")
                    break

                # Parse the request to get the request code and parameters
                request_code, request_parameters = network_handler.parse_request(
                    request)

                response = str()

                if not is_valid_request_code(request_code):
                    print(f'invalid request code: {request_code}')
                    response = network_handler.handle_unknown_request()

                if request_code == REGISTRATION_REQUEST:
                    response = network_handler.handle_registration_request(
                        request_parameters)

                elif request_code == RECONNECT_REQUEST:
                    response = network_handler.handle_reconnect_request(
                        request_parameters)

                elif request_code == KEYS_EXCHANGE_REQUEST:
                    response = network_handler.handle_key_exchange_request(
                        request_parameters)

                elif request_code == FILE_TRANSFER_REQUEST:
                    response = network_handler.handle_file_transfer_request(
                        request_parameters)

                elif request_code == VALID_CKSUM_FINISH_REQUEST:
                    response = network_handler.handle_cksum_finish_request(
                        request_parameters, request_code)

                elif request_code == INVALID_CKSUM_RESEND_REQUEST:
                    network_handler.handle_invalid_cksum_request(
                        request_parameters)
                    continue  # skip to the next iteration and don't send a response

                elif request_code == INVALID_CKSUM_FINISH_REQUEST:
                    response = network_handler.handle_cksum_finish_request(
                        request_parameters, request_code)

                else:  # unknown request code
                    response = network_handler.handle_unknown_request(
                        request_parameters)
            except Exception as e:
                print(e)
                response = network_handler.handle_unknown_request(
                    request_parameters)

            # Send response to client
            client_connect.send(response.encode())
            print(f'RESPONSE SENT: {response.encode()}')

        client_connect.close()
