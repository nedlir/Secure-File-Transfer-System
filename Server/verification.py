import re
import uuid


def is_valid_request_code(request_code):
    # Verify that request_code is a valid 4-digit numerical value.

    if len(str(request_code)) != 4:
        return False
    try:
        int(request_code)
        return True
    except ValueError:
        return False


def is_valid_client_id(client_id):
    # Verify that client_id is a valid UUID represented in hex.

    try:
        uuid.UUID(client_id, version=4)
        return True
    except ValueError:
        return False


def is_valid_client_name(client_name):
    # Verify that client_name only contains numbers, alphanumeric characters, and spaces.

    pattern = r'^[\w\s]+$'
    return bool(re.match(pattern, client_name))
