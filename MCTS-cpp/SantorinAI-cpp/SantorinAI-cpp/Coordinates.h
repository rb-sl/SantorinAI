#pragma once

#include "Message.h"

class Coordinates
{
public:
	int row;
	int column;
	
	Coordinates();
	Coordinates(int row, int column);	

	bool operator==(const Coordinates other);
	bool operator!=(const Coordinates other);
	bool operator<(const Coordinates other) const;
};

const Coordinates null_coordinate = Coordinates(-1, -1);

