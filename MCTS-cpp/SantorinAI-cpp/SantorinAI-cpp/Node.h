#pragma once

#include <iostream>
#include <vector>
#include <map>

#include "State.h"
#include "Message.h"

class Node
{
private:
	const int ALPHA = 2;

	State state;
	std::string action;
	std::string message;

	Node* parent;
	//std::map<Node*, float> children;
	std::vector<Node*> children;

	int n_wins;
	int n_sims;
	float ucb1;
public:
	// Root constructor
	Node(State s);
	// Children constructor
	Node(State s, Node* parent, std::string action, std::string message);
	State* get_state();
	void set_parent(Node* parent);
	Node* get_parent();

	Node* node_update(std::map<coord, block> board_update, std::string active_player);
	Node* node_update(update up);

	bool has_children();
	std::vector<Node*> get_children();
	Node* add_child(State* state, std::string action, std::string message);

	float get_ucb1();
	void update_ucb1();

	void print_tree(int n_tabs);
};

