#include "AI.h"

#include <iostream>

#include <map>

using namespace std;

AI::AI(string self) : root(State()), current_node(&root) {
	// Players initialization
	this->nickname = self;

	// Random components initialization
	rng = mt19937(rd());
}

void AI::set_players(vector<string> player_list)
{
	this->player_list = vector<string>(player_list);
	for (auto player : player_list) {
		if (player != this->nickname)
			this->opponent = player;
	}
}

Node* AI::add_node(State* state, string action, string message) {
	int hash = state->hash();

	try {
		vector<Node*> bucket = this->closed_list.at(hash);
		for (Node* elem : bucket) {
			if (elem->get_state()->operator==(state)) {
				return elem;
			}
		}
	}
	catch (out_of_range e) {
		cout << "Creating new bucket " << hash << endl;
	}

	Node* new_node = this->current_node->add_child(state, action, message);
	this->closed_list[hash].insert(this->closed_list[hash].begin(), new_node);
	return new_node;
}

string AI::choose_starter() {
	uniform_int_distribution<mt19937::result_type> dist(0, this->player_list.size() - 1);

	string starter = player_list.at(dist(rng));
	this->set_turn(starter);

	return starter;
}

void AI::set_turn(string active_player) {
	string waiting = active_player == this->nickname ? this->opponent : this->nickname;
	this->current_node->get_state()->set_active_player(active_player);
	this->current_node->get_state()->set_waiting_player(waiting);
}

void AI::server_update(update update) {
	string player = update.player;
	State current_state = this->current_node->get_state();
	State candidate_state = State(current_state);
	map<coord, block> board_update = update.board_update;

	candidate_state.set_active_player(player);
	candidate_state.increase_time();

	bool flag = false;
	for (auto& elem : update.reachable_cells) {
		if (!elem.second.empty()) {
			flag = true;
			break;
		}
	}
	candidate_state.set_can_move(flag);

	flag = false;
	for (auto& elem : update.buildable_cells) {
		if (!elem.second.empty()) {
			flag = true;
			break;
		}
	}
	candidate_state.set_can_build(flag);

	// In case of pass resets has_ variables
	if (player != current_state.get_active_player()) {
		candidate_state.set_can_move(true);
		candidate_state.set_has_moved(false);
		candidate_state.set_can_build(false);
		candidate_state.set_has_built(false);

		candidate_state.reset_moved_worker();
	}

	for (const auto& tuple : board_update) {
		coord c = tuple.first;
		block to_update = tuple.second;

		candidate_state.update_board(c, to_update);
	}
	candidate_state.print_board();

	this->current_node = add_node(&candidate_state, "UPDATE", "");

	this->root.print_tree(0);
}

vector<Action> AI::get_actions(State* state) {
	return get_actions(this->nickname, state);
}

vector<Action> AI::get_actions(string player, State* state) {
	vector<Action> actions;
	vector<Action> temp_actions;

	// PLACE
	temp_actions = state->placeable_cells(player);
	actions.insert(actions.end(), temp_actions.begin(), temp_actions.end());

	// MOVE
	temp_actions = state->reachable_cells(player);
	actions.insert(actions.end(), temp_actions.begin(), temp_actions.end());

	// Build
	temp_actions = state->buildable_cells(player);
	actions.insert(actions.end(), temp_actions.begin(), temp_actions.end());

	// Pass
	if (state->can_pass()) {
		actions.push_back(Action(ActionType::PASS));
	}

	// Lose
	if (actions.size() == 0) {
		actions.push_back(Action(ActionType::LOSE));
	}

	return actions;
}

string AI::choose_action() {
	State* state = this->current_node->get_state();

	vector<Action> actions = get_actions(state);

	Action chosen_action = random_action(actions);

	string message = "";
	string id;
	State next_state;

	switch (chosen_action.get_type()) {
	case ActionType::PLACE:
		if (state->get_workers()[state->get_active_player()].size() == 0) {
			id = 'M';
		}
		else {
			id = 'F';
		}
		message = "{\"type\":\"WORKERINIT\",\"message\":\"{\\\"coordinates\\\":{\\\"row\\\":" 
			+ to_string(chosen_action.get_target().row) + ",\\\"column\\\":"
			+ to_string(chosen_action.get_target().column) + "},\\\"sex\\\":\\\""
			+ id + "\\\",\\\"player\\\":\\\"" + this->nickname + "\\\"}\"}";

		next_state = state->place("SantorinAI", id, chosen_action.get_target());
		this->current_node = add_node(&next_state, "PLACE", message);
		break;
	case ActionType::MOVE:
		message = "{\"type\":\"MOVE\",\"message\":\"{\\\"source\\\":{\\\"row\\\":"
			+ to_string(chosen_action.get_source().row) + ",\\\"column\\\":" 
			+ to_string(chosen_action.get_source().column) + "},\\\"destination\\\":{\\\"row\\\":"
			+ to_string(chosen_action.get_target().row) + ",\\\"column\\\":"
			+ to_string(chosen_action.get_target().column) + "},\\\"player\\\":\\\"" + this->nickname + "\\\"}\"}";

		next_state = state->move(chosen_action.get_source(), chosen_action.get_target());
		this->current_node = add_node(&next_state, "MOVE", message);
		break;
	case ActionType::BUILD:
		message = "{\"type\":\"BUILD\",\"message\":\"{\\\"source\\\":{\\\"row\\\":"
			+ to_string(chosen_action.get_source().row) + ",\\\"column\\\":"
			+ to_string(chosen_action.get_source().column) + "},\\\"destination\\\":{\\\"row\\\":"
			+ to_string(chosen_action.get_target().row) + ",\\\"column\\\":"
			+ to_string(chosen_action.get_target().column) + "},\\\"level\\\":"
			+ to_string(chosen_action.get_level()) + ",\\\"player\\\":\\\"" + this->nickname + "\\\"}\"}";

		next_state = state->build(chosen_action.get_source(), chosen_action.get_target(), chosen_action.get_level());
		this->current_node = add_node(&next_state, "BUILD", message);
		break;
	case ActionType::PASS:
		message = "{\"type\":\"PASS\",\"message\":\"{\\\"player\\\":\\\"" + this->nickname + "\\\"}\"}";

		next_state = state->pass();
		this->current_node = add_node(&next_state, "PASS", message);
		break;
	case ActionType::LOSE:
		message = "{\"type\":\"LOSE\",\"message\":\"{\\\"player\\\":\\\"" + this->nickname + "\\\"}\"}";
		break;
	}
	
	cout << "CHOSEN ACTION " << message << endl;

	return message;
}

Action AI::random_action(vector<Action> actions) {
	uniform_int_distribution<mt19937::result_type> dist(0, actions.size() - 1);
	return actions[dist(this->rng)];
}

Action AI::MC_action(vector<Action> actions) {
	for (int i = 0; i < N_ITERATIONS; i++) {
		Node* leaf = MC_selection();
		MC_expansion(leaf);
	}
	return actions[0];
}

Node* AI::MC_selection() {
	Node* node = &this->root;

	float best_score;
	vector<Node*> best_children;

	while (node->has_children()) {
		best_score = -INFINITY;
		best_children.clear();

		for (auto child : node->get_children()) {
			if (child->get_ucb1() > best_score) {
				best_score = child->get_ucb1();
				best_children.clear();
				best_children.push_back(child);
			}
			else if (child->get_ucb1() == best_score) {
				best_children.push_back(child);
			}
		}

		uniform_int_distribution<mt19937::result_type> dist(0, best_children.size() - 1);
		node = node->get_children().at(dist(this->rng));
	}

	return node;
}

void AI::MC_expansion(Node* node) {
	State* state = node->get_state();
	State next_state;
	string id;

	for (auto action : this->get_actions(state->get_active_player(), state)) {
		switch (action.get_type()) {
		case ActionType::PLACE:
			if (state->get_workers()[state->get_active_player()].size() == 0) {
				id = 'M';
			}
			else {
				id = 'F';
			}
			next_state = state->place(state->get_active_player(), id, action.get_target());
		case ActionType::MOVE:
			next_state = state->move(action.get_source(), action.get_target());
			break;
		case ActionType::BUILD:
			next_state = state->build(action.get_source(), action.get_target(), action.get_level());
			break;
		case ActionType::PASS:
			next_state = state->pass();
			break;
		case ActionType::LOSE:
			break;
		}
		
		node->add_child(&next_state, "sim", "");
	}
}

