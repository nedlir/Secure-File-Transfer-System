#pragma once

#include <iostream>
#include <string>
#include <fstream>
#include <vector>

#include <stdlib.h>

#include <boost/asio.hpp>
#include <boost/algorithm/string.hpp>

#include "constants.h"

#include "EncryptionHandler.h"
#include "FilesHandler.h"
#include "NetworkHandler.h"
#include "RequestsGenerator.h"
#include "StringHandler.h"

class Protocol {
public:
    bool handle_server_responses(boost::asio::ip::tcp::socket& socket);

private:
    int string_to_int(const std::string& str);

    std::string file_path;
    std::string file_name;
    std::string client_name;
    std::string client_uuid;

    std::string private_key;
    std::string public_key;
    std::string aes_key;

    FilesHandler files_handler;
    EncryptionHandler encryption_handler;

    std::vector<std::string> response_data;
    size_t response;
    size_t file_transfer_attempts = 0;
};