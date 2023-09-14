#pragma once

#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <sstream>
#include "constants.h"

struct Request {

    // Header
    std::string client_uuid;
    size_t version = 0;
    uint16_t request_code = 0;
    uint32_t payload_size = 0;

    // Payload
    std::string client_name;
    std::string public_key;
    uint32_t file_size = 0;
    std::string file_name;
    std::string file_content;
};

class RequestsGenerator
{
public:

    // Public functions
    RequestsGenerator(const std::string& client_name);

    void generate_request(Request& request, size_t request_code);

    // Setters
    void set_client_uuid(const std::string &client_id);
    void set_client_name(const std::string &client_name);
    void set_public_key(const std::string& public_key);
    void set_file_size(uint32_t file_size);
    void set_file_name(const std::string& file_name);
    void set_file_content(const std::string& file_content);

private:

    // Private variables
    std::string client_uuid;
    std::string client_name;
    std::string public_key;
    uint32_t file_size;
    std::string file_name;
    std::string file_content;

    // Private funcitons
    RequestsGenerator();

    void get_registration_request_payload(Request &request);
    void get_keys_exchange_request_payload(Request& request);
    void get_reconnect_request_payload(Request& request);
    void get_file_transfer_request_payload(Request& request);
    void get_valid_cksum_request_payload(Request& request);
    void get_invalid_cksum_resend_request_payload(Request& request);
    void get_invalid_cksum_finish_request_payload(Request& request);

};
