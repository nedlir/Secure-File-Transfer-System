import socket
import threading

from files_handler import FilesHandler
from protocol import Protocol


MAX_CONNECTIONS_PER_IP = 5


def run_server():
    files_handler = FilesHandler()
    # Read the port number from the file 'port.info'
    port = files_handler.get_port_number()
    try:
        # Listen for incoming connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('localhost', port))

            server_socket.listen()

            print(f"Server is listening on port {port}...")

            # Dictionary to keep track of the number of connections per each IP address
            connections_per_ip = {}

            while True:
                # Wait for a client to create a connection
                client_connect, client_address = server_socket.accept()

                # Check if the IP address of the client has exceeded the connection limit
                if client_address[0] in connections_per_ip:
                    # set threshold to 10 connections
                    if connections_per_ip[client_address[0]] >= MAX_CONNECTIONS_PER_IP:
                        print(f"Refusing connection from {client_address[0]}")
                        client_connect.close()
                        continue
                    else:  # Additional connection from client:
                        connections_per_ip[client_address[0]
                                           ] = connections_per_ip[client_address[0]] + 1
                else:  # This is first time client connects
                    connections_per_ip[client_address[0]] = 1

                # Handle each client request in a separate thread
                threading.Thread(target=Protocol.handle_client_requests,
                                 args=(client_connect, client_address)).start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Server shutting down...")


run_server()
