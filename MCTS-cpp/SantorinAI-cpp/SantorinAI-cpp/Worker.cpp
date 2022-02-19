#include "Worker.h"

using namespace std;

Worker::Worker(){
	this->owner = "DEFAULT";
}

Worker::Worker(string owner, string id, Coordinates coordinates) {
	this->owner = owner;
	this->id = id;
	this->coordinates = coordinates;
}

Worker::Worker(const Worker* worker) {
	this->owner = worker->owner;
	this->id = worker->id;
	this->coordinates = worker->coordinates;
}

std::string Worker::get_owner() {
	return this->owner;
}

std::string Worker::get_id() {
	return this->id;
}

Coordinates Worker::get_coordinates() {
	return this->coordinates;
}

void Worker::set_coordinates(Coordinates coordinates) {
	this->coordinates = coordinates;
}

bool Worker::operator==(Worker* other) {
	return this->owner == other->owner && this->id == other->id;
}

