#include <stdlib.h>

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "EncryptionHandler.h"
#include "FilesHandler.h"
#include "Protocol.h"
#include "NetworkHandler.h"


void connect_to_server(const std::string& server_ip, const std::string& port, boost::asio::io_context& io_service, boost::asio::ip::tcp::socket& socket)
{
	boost::asio::ip::tcp::resolver resolver(io_service);
	boost::asio::ip::tcp::resolver::query query(server_ip, port);
	boost::asio::ip::tcp::resolver::iterator endpoint_iterator = resolver.resolve(query);
	socket.connect(*endpoint_iterator);
}

int main()
{
	// Read IP and Port from files
	std::string server_ip;
	std::string port;
	FilesHandler files_handler;
	try
	{
		server_ip = files_handler.read_ip_address();
		port = files_handler.read_port();
	}
	catch (std::exception& e)
	{
		std::cerr << "Error: " << e.what() << std::endl;
		return EXIT_FAILURE;
	}

	// Connect to server
	boost::asio::io_service io_service;
	boost::asio::ip::tcp::socket socket(io_service);
	try
	{
		connect_to_server(server_ip, port, io_service, socket);
	}
	catch (std::exception& e)
	{
		std::cerr << "Error: " << e.what() << std::endl;
		return EXIT_FAILURE;
	}

	// Execute protocol
	Protocol protocol;
	bool server_communication_success = protocol.handle_server_responses(socket);

	// Disconnect from server
	socket.close();
	if (server_communication_success)
	{
		std::cout << "Disconnected from server succesfuly." << std::endl;
		return EXIT_SUCCESS;
	}
	else
	{
		std::cout << "Disconnected from server with an error." << std::endl;
		return EXIT_FAILURE;
	}
}
