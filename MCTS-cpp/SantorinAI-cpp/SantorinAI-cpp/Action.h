#pragma once

#include "Coordinates.h"

enum class ActionType { PLACE, MOVE, BUILD, PASS, LOSE };

class Action {
private:
	ActionType type;
	Coordinates source;
	Coordinates target;
	int level;
public:	
	Action(ActionType type);
	Action(ActionType type, Coordinates target);
	Action(ActionType type, Coordinates source, Coordinates target);
	Action(ActionType type, Coordinates source, Coordinates target, int level);

	ActionType get_type();
	Coordinates get_source();
	Coordinates get_target();
	int get_level();
};