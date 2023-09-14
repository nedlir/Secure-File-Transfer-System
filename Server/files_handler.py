import os


class FilesHandler:
    PORT_FILE = "port.info"
    DEFAULT_PORT = 1234
    MIN_PORT = 1
    MAX_PORT = 65535

    def __init__(self):
        self.port = self.get_port_number()

    # load port number from file
    def get_port_number(self):
        try:
            with open(self.PORT_FILE, 'r') as f:
                port = int(f.readline())
                if port < self.MIN_PORT or port > self.MAX_PORT:
                    raise ValueError('Invalid port number')
                return port
        except (FileNotFoundError, ValueError):
            print(
                f'Invalid port number or {self.PORT_FILE} file not found. Using default port {self.DEFAULT_PORT}.')
            return self.DEFAULT_PORT

    def save_decrypted_file(self, client_name, file_name, decrypted_file_content):
        client_dir = os.path.abspath(client_name)
        if not os.path.exists(client_dir):
            os.makedirs(client_dir)
        file_path = os.path.abspath(os.path.join(client_dir, file_name))
        if not os.access(os.path.dirname(file_path), os.W_OK):
            raise IOError(f'Permission denied: {os.path.dirname(file_path)}')
        sanitized_file_name = os.path.basename(file_path)
        with open(file_path, "wb") as f:
            f.write(decrypted_file_content)
        print(f"File saved: {sanitized_file_name}")
