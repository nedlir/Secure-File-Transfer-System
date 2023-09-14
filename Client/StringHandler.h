#pragma once

#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "constants.h"
#include "RequestsGenerator.h"


class StringHandler
{
public:
	std::string serialized_request(const Request& request);
	int string_to_int(const std::string& str);
	std::vector<std::string> split_string(std::string str, char delimiter);

};

