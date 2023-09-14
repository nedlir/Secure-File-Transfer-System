#include "StringHandler.h"

std::string StringHandler::serialized_request(const Request& request) {
    std::ostringstream oss;

    // Header
    oss << request.client_uuid << ":";
    oss << request.version << ":";
    oss << request.request_code << ":";
    oss << request.payload_size << ":";

    // Payload
    if (!request.client_name.empty())
        oss << request.client_name << ":";
    if (!request.public_key.empty())
        oss << request.public_key << ":";
    if (request.file_size != 0)
        oss << request.file_size << ":";
    if (!request.file_name.empty())
        oss << request.file_name << ":";
    if (!request.file_content.empty())
        oss << request.file_content << ":";

    std::string message = oss.str();
    if (!message.empty()) // Remove the trailing ':' from the message
        message.pop_back();

    return message;
}

// Converts string to integer
int StringHandler::string_to_int(const std::string& str)
{
    try
    {
        int num = std::stoi(str);
        return num;
    }
    catch (const std::exception& e)
    {
        // handle the case where the input string is not a valid integer or out of range for an integer
        return RESPONSE::INVALID_REQUEST;
    }
}


std::vector<std::string> StringHandler::split_string(std::string str, char delimiter)
{
    std::vector<std::string> words;
    std::string word;
    for (char c : str)
    {
        if (c == delimiter)
        { // if the character is delimiter add the current word to the vector and start new word
            words.push_back(word);
            word = "";
        }
        else
        { // add character to the current word
            word = word + c;
        }
    }
    if (word.length() > 0)
    { // if there is a word left in the temp string
        words.push_back(word);
    }
    return words;
}