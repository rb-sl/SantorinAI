#pragma once

#include <iostream>
#include <vector>
#include <map>

#include "Coordinates.h"
#include "Block.h"
#include "Action.h"

class State
{
private:
	// Counter for blocks built (~nturns)
	unsigned int time;

	std::string active_player;
	std::string waiting_player;

	bool can_move;
	bool can_build;
	bool has_moved;
	bool has_built;
	std::string moved_worker;

	bool transformed;

	std::vector<std::vector<Block>> board;

	// Workers in state, e.g. {"player":{"id":Coordinates}}
	std::map<std::string, std::map<std::string, Worker>> workers;

	void reflectX();
	void reflectY();
	void reflectXY();
public:
	State();
	State(std::string active_player);
	State(const State* state);

	void increase_time();

	std::string get_active_player();
	void set_active_player(std::string active_player);
	std::string get_waiting_player();
	void set_waiting_player(std::string active_player);

	void set_can_move(bool can_move);
	void set_can_build(bool can_build);
	void set_has_moved(bool has_moved);
	void set_has_built(bool has_built);

	void reset_moved_worker();

	bool is_transformed();
	State get_reduced();

	void update_board(coord c, block b);

	std::map<std::string, std::map<std::string, Worker>> get_workers();
	
	bool can_place();
	bool can_place(Coordinates c);
	bool can_place(std::string player);
	bool can_place(std::string player, Coordinates c);
	bool can_place(std::string player, int row, int column);
	std::vector<Action> placeable_cells();
	std::vector<Action> placeable_cells(std::string player);
	State place(std::string player, std::string worker_id, Coordinates dst);

	std::vector<Action> reachable_cells();
	std::vector<Action> reachable_cells(std::string player);
	State move(Coordinates src, Coordinates dst);

	std::vector<Action> buildable_cells(std::string player);
	State build(Coordinates src, Coordinates dst, int level);

	bool can_pass();
	bool can_pass(std::string player);	
	State pass();

	void print_board();

	int hash();

	bool operator==(State* other);
};
