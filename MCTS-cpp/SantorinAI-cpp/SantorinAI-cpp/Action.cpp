#include "Action.h"

using namespace std;

Action::Action(ActionType type) : Action::Action(type, null_coordinate, null_coordinate, -1) {}

Action::Action(ActionType type, Coordinates target) : Action::Action(type, null_coordinate, target, -1) {}

Action::Action(ActionType type, Coordinates source, Coordinates target) : Action(type, source, target, -1) {}

Action::Action(ActionType type, Coordinates source, Coordinates target, int level) {
	this->type = type;
	this->source = source;
	this->target = target;
	this->level = level;
}

ActionType Action::get_type() {
	return this->type;
}

Coordinates Action::get_source() {
	return this->source;
}

Coordinates Action::get_target() {
	return this->target;
}

int Action::get_level() {
	return this->level;
}
