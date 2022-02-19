#pragma once
#include "Coordinates.h"

class Worker {
private:
	std::string owner;
	std::string id;
	Coordinates coordinates;
public:
	Worker();
	Worker(std::string owner, std::string id, Coordinates coordinates);
	Worker(const Worker* worker);

	std::string get_owner();
	std::string get_id();
	Coordinates get_coordinates();

	void set_coordinates(Coordinates coordinates);

	bool operator==(Worker* other);
};
