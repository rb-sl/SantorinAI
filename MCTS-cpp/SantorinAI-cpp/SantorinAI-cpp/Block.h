#pragma once

#include <iostream>
#include <vector>

#include "Coordinates.h"
#include "Worker.h"

class Block
{
private:
	Coordinates real;
	std::vector<int> levels;
	std::string worker_owner;
	std::string worker_id;
public:
	Block(Coordinates real);
	Block(const Block* block);
	void set_levels(std::vector<int> level);
	void add_level(int level);
	int get_top_level();
	Coordinates get_real_coord();

	std::string get_worker_owner();
	std::string get_worker_id();
	void place_worker(Worker* worker);	
	void remove_worker();
	bool has_worker();
};

