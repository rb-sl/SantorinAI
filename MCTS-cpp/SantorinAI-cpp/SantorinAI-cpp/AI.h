#pragma once

#include <iostream>
#include <vector>
#include <set>
#include <random>

#include "State.h"
#include "Action.h"
#include "Message.h"
#include "Node.h"

class AI
{
private:
	std::string nickname;
	std::string opponent;
	std::vector<std::string> player_list;

	std::random_device rd;
	std::mt19937 rng;

	std::map<int, std::vector<Node*>> closed_list;

	Node root;
	Node* current_node;

	int N_ITERATIONS = 1000;

	Node* add_node(State* state, std::string action, std::string message);
	Action random_action(std::vector<Action> actions);

	Action MC_action(std::vector<Action> actions);
	Node* MC_selection();
	void MC_expansion(Node* node);
public:
	AI(std::string self);
	void set_players(std::vector<std::string> player_list);
	std::string choose_starter();
	void set_turn(std::string starter);
	//void server_update(std::map<coord, block> board_update, std::string active_player);
	void server_update(update update);

	std::vector<Action> get_actions(State* state);
	std::vector<Action> get_actions(std::string player, State* state);
	std::string choose_action();
};
