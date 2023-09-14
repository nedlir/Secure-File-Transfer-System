#pragma once

#include <fstream>
#include <iostream>
#include <sstream>
#include <cstring>
#include <regex>
#include <string>
#include <vector>

#include <memory>
#include <iomanip>
#include <cstdint>

#include <boost/algorithm/string.hpp>
#include <boost/asio.hpp>
#include <boost/bind/bind.hpp>
#include <boost/crc.hpp>
#include <boost/filesystem.hpp>


#include "constants.h"

class FilesHandler {
public:
    FilesHandler() = default;
    ~FilesHandler() = default;

    bool init_variables_from_files(std::string& client_name, std::string& client_uuid, std::string& private_key, std::string& file_path, std::string& file_name);
    bool is_file_exist(const std::string& filename);
    std::string read_client_name();
    std::string read_client_uuid();
    std::string read_private_key();
    std::string read_ip_address();
    std::string read_port();
    std::string read_filepath();
    std::string calculate_crc(const std::string& file_path);
    void create_me_file(std::string client_name, std::string client_uuid, std::string private_key);


};
