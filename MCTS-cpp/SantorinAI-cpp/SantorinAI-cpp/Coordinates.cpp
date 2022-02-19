#include "Coordinates.h"
#include "Message.h"

Coordinates::Coordinates()
{
    this->row = -1;
    this->column = -1;
}

Coordinates::Coordinates(int row, int column)
{
    this->row = row;
    this->column = column;
}

bool Coordinates::operator==(const Coordinates other)
{
    return this->row == other.row and this->column == other.column;
}

bool Coordinates::operator!=(const Coordinates other)
{
    return !(*this == other);
}

/// <summary>
/// Comparison for maps using coordinates; needs a total ordering
/// </summary>
/// <param name="other">The object to compare against</param>
/// <returns>True if this &lt; other</returns>
bool Coordinates::operator<(const Coordinates other) const {
    return this->row * 5 + this->column < other.row * 5 + other.column;
}
