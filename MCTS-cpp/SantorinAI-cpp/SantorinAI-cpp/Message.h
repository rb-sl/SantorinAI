#pragma once

#include <iostream>
#include <map>
#include <unordered_map>
#include <vector>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct envelope {
	std::string type;
	std::string message;
};

struct serverstate {
	bool open;
	bool active;
};

struct players {
	std::map<std::string, std::string> player_map;
	std::string active_player;
};

struct endgame {
	bool is_winner;
	std::string player;
};

struct coord {
	int row;
	int column;
	bool operator<(const coord& rhs) const;
};

struct block {
	std::vector<int> level_list;
	std::string worker_owner;
	std::string worker_id;
};

// Update of agent turn
struct update {
	std::map<coord, block> board_update;
	std::map<coord, std::vector<coord>> reachable_cells;
	std::map<coord, std::map<coord, std::vector<int>>> buildable_cells;
	bool can_place;
	bool can_pass;
	bool can_undo;
	std::string player;
};

void to_json(json& j, const envelope& m);
void from_json(const json& j, envelope& m);

void to_json(json& j, const serverstate& m);
void from_json(const json& j, serverstate& m);

void to_json(json& j, const players& m);
void from_json(const json& j, players& m);

void to_json(json& j, const endgame& m);
void from_json(const json& j, endgame& m);

void to_json(json& j, const update& m);
void from_json(const json& j, update& m);

void to_json(json& j, const coord& c);
void from_json(const json& j, coord& c);

void to_json(json& j, const block& c);
void from_json(const json& j, block& c);
