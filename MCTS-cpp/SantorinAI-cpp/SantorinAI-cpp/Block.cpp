#include "Block.h"

#include <algorithm>

using namespace std;

Block::Block(Coordinates real) {
	this->real = real;
	this->levels.push_back(0);
	this->worker_owner = "";
	this->worker_id = "";
}

Block::Block(const Block* block) {
	this->real = block->real;
	this->levels = vector<int>(block->levels);
	this->worker_owner = block->worker_owner;
	this->worker_id = block->worker_id;
}

void Block::set_levels(std::vector<int> levels) {
	this->levels = vector<int>(levels);
}

void Block::add_level(int level) {
	this->levels.insert(this->levels.begin(), level);
}

int Block::get_top_level() {
	return this->levels[0];
}

Coordinates Block::get_real_coord() {
	return this->real;
}

void Block::place_worker(Worker* worker) {
	this->worker_owner = worker->get_owner();
	this->worker_id = worker->get_id();
}

string Block::get_worker_owner()
{
	return this->worker_owner;
}

string Block::get_worker_id()
{
	return this->worker_id;
}

void Block::remove_worker()
{
	this->worker_owner = "";
	this->worker_id = "";
}

bool Block::has_worker()
{
	return this->worker_owner != "";
}
