#include "Protocol.h"

bool Protocol::handle_server_responses(boost::asio::ip::tcp::socket& socket)
{
	// Variables from me.info and transfer.info files
	if (!files_handler.init_variables_from_files(client_name, client_uuid, private_key, file_path, file_name))
		return false;

	if (!files_handler.is_file_exist(file_path))
	{
		std::cerr << "Failed to open file. Invalid filepath or file doesn't exist." << std::endl;
		return false;
	}
		

	NetworkHandler network_handler(client_name);
	StringHandler string_handler;

	if (!network_handler.send_registration_or_reconnection_request(socket, client_name, client_uuid))
		return false;

	while (true) {
		if (!network_handler.read_server_response(socket, response_data))
			return false;

		response = string_handler.string_to_int(response_data.at(1));

		if (response == RESPONSE::REGISTRATION_ACCEPT)
		{
			// Create me.info file
			client_uuid = response_data.at(3);
			private_key = encryption_handler.get_private_key();
			files_handler.create_me_file(client_name, client_uuid, private_key);

			// Send public key to the server.
			if (!network_handler.send_public_key_request(socket, encryption_handler, client_uuid))
				return false;
		}

		else if (response == RESPONSE::REGISTRATION_FAIL)
		{
			// Registration failed because the name is already in use
			std::cerr << "Error: Registration failed, username is already in use." << std::endl;
			return false;
		}

		else if (response == RESPONSE::RECONNECT_FAIL)
		{
			std::cerr << "Error: Reconnection failed, username or public key not found. Try to delete or change " << FILES::ME_FILE << std::endl;
			return false;
		}

		else if (response == RESPONSE::RSA_KEY_ACCEPT || response == RESPONSE::RECONNECT_ACCEPT)
		{
			aes_key = encryption_handler.decrypt_AES_key_with_private_RSA_key(response_data.at(4), private_key);

			if (!network_handler.send_file_request(socket, file_path, encryption_handler, aes_key, response_data))
				return false;
			else
				file_transfer_attempts++;
		}

		else if (response == RESPONSE::FILE_TRANSFER_SUCCESS)
		{
			if (!network_handler.handle_file_transfer_success(socket, encryption_handler, files_handler,
				file_path, aes_key, response_data, file_transfer_attempts))
				return false;
		}

		else if (response == RESPONSE::CRC_FINISH)
		{
			return true;
		}
		else
		{
			std::cerr << "Error: unexpected response code " << response << std::endl;
			return false;
		}
	}
}
