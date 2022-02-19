#include "State.h"
#include <vector>
using namespace std;

#include "Block.h"
#include "Colors.h"

State::State() : State("") {}

State::State(string active_player) {
	this->active_player = active_player;

	time = 0;
	this->can_move = true;
	this->can_build = false;
	this->has_moved = false;
	this->has_built = false;
	this->moved_worker = "";

	this->transformed = false;

	for (int i = 0; i < 5; i++) {
		vector<Block> row;
		for (int j = 0; j < 5; j++) {
			row.push_back(Block(Coordinates(i, j)));
		}
		this->board.push_back(row);
	}
}

State::State(const State* state) {
	this->active_player = state->active_player;
	this->waiting_player = waiting_player;

	time = state->time + 1;
	this->can_move = state->can_move;
	this->can_build = state->can_build;
	this->has_moved = state->has_moved;
	this->has_built = state->has_built;

	this->moved_worker = state->moved_worker;

	this->transformed = state->transformed;

	for (int i = 0; i < 5; i++) {
		vector<Block> row;
		for (int j = 0; j < 5; j++) {
			row.push_back(Block(state->board[i][j]));
		}
		this->board.push_back(row);
	}

	for (const auto& worker_tuple : state->workers) {
		string player = worker_tuple.first;
		map<string, Worker> worker_map = worker_tuple.second;

		for (const auto& elem : worker_map) {
			string id = elem.first;
			Worker worker = elem.second;

			this->workers[player][id] = Worker(&worker);
		}
	}
}

void State::increase_time() {
	this->time++;
}

std::string State::get_active_player() {
	return this->active_player;
}

void State::set_active_player(std::string active_player) {
	this->active_player = active_player;
}

std::string State::get_waiting_player() {
	return this->waiting_player;
}

void State::set_waiting_player(std::string waiting_player) {
	this->waiting_player = waiting_player;
}


bool State::is_transformed() {
	return this->transformed;
}

void State::set_can_move(bool can_move) {
	this->can_move = can_move;
}

void State::set_can_build(bool can_build) {
	this->can_build = can_build;
}

void State::set_has_moved(bool has_moved) {
	this->has_moved = has_moved;
}

void State::set_has_built(bool has_built) {
	this->has_built = has_built;
}

void State::reset_moved_worker() {
	this->moved_worker = "";
}

void State::update_board(coord c, block b) {
	this->board[c.row][c.column].set_levels(b.level_list);

	if (b.worker_id != "") {
		Worker* worker;
		try {
			worker = &this->workers.at(b.worker_owner).at(b.worker_id);
		}
		catch (std::out_of_range e) {
			this->workers[b.worker_owner][b.worker_id] = Worker(b.worker_owner, b.worker_id, Coordinates(c.row, c.column));
			worker = &this->workers[b.worker_owner][b.worker_id];
		}
		worker->set_coordinates(Coordinates(c.row, c.column));
		this->board[c.row][c.column].place_worker(worker);
	}
	else {
		this->board[c.row][c.column].remove_worker();
	}
}

map<string, map<string, Worker>> State::get_workers() {
	return this->workers;
}

// --------------------------
// Functions for action PLACE
// --------------------------

// Checks if the agent can place a worker
bool State::can_place() {
	return can_place("SantorinAI");
}

// Checks if the agent can place a worker at the given coordinates
bool State::can_place(Coordinates c) {
	return can_place("SantorinAI", c);
}

// Checks if the given player can place a worker
bool State::can_place(string player) {
	return this->active_player == player and this->workers[player].size() < 2;
}

// Checks if the given player can place a worker at the given coordinates
bool State::can_place(string player, Coordinates c) {
	return can_place(player, c.row, c.column);
}

bool State::can_place(string player, int row, int column) {
	return this->can_place(player) and !this->board[row][column].has_worker();
}

vector<Action> State::placeable_cells() {
	return placeable_cells("SantorinAI");
}

/// <summary>
/// Computes the list of cells where workers can be placed
/// </summary>
/// <param name="player">The active player</param>
/// <returns>The vector of available PLACE actions</returns>
vector<Action> State::placeable_cells(std::string player) {
	vector<Action> placeable;

	if (this->workers[player].size() == 2) {
		return placeable;
	}

	for (int i = 0; i < 5; i++) {
		for (int j = 0; j < 5; j++) {
			if (can_place(player, i, j)) {
				placeable.push_back(Action(ActionType::PLACE, Coordinates(i, j)));
			}
		}
	}

	return placeable;
}

// Applies the action PLACE and returns a new state
State State::place(string player, string worker_id, Coordinates target) {
	State next_state = State(this);
	
	next_state.workers[player][worker_id] = Worker(player, worker_id, target);
	next_state.board[target.row][target.column].place_worker(&next_state.workers[player][worker_id]);
	
	return next_state;
}

// -------------------------
// Functions for action MOVE
// -------------------------

vector<Action> State::reachable_cells() {
	return reachable_cells("SantorinAI");
}

/// <summary>
/// Computes the available MOVE actions
/// </summary>
/// <param name="player">The active player</param>
/// <returns>The list of available MOVE actions</returns>
vector<Action> State::reachable_cells(string player) {
	vector<Action> reachable;

	if (player != this->active_player or this->has_moved or this->can_place()) {
		return reachable;
	}

	for (auto& worker_tuple : this->workers.at(player)) {
		string worker_id = worker_tuple.first;
		Worker worker = worker_tuple.second;

		for (int i = worker.get_coordinates().row - 1; i <= worker.get_coordinates().row + 1; i++) {
			for (int j = worker.get_coordinates().column - 1; j <= worker.get_coordinates().column + 1; j++) {
				if (i >= 0 and i < 5 and j >= 0 and j < 5 
						and (i != worker.get_coordinates().row or j != worker.get_coordinates().column)
						and not this->board[i][j].has_worker()
						and this->board[i][j].get_top_level() < 4) {
					reachable.push_back(Action(ActionType::MOVE, worker.get_coordinates(), Coordinates(i, j)));
				}
			}
		}
	}

	return reachable;
}

State State::move(Coordinates src, Coordinates dst) {
	State next_state = State(this);

	Block* source = &next_state.board[src.row][src.column];
	string worker_owner = source->get_worker_owner();
	string worker_id = source->get_worker_id();

	Worker* worker = &next_state.workers[worker_owner][worker_id];
	worker->set_coordinates(dst);

	source->remove_worker();
	next_state.board[dst.row][dst.column].place_worker(worker);

	next_state.has_moved = true;
	next_state.moved_worker = worker_id;

	next_state.can_move = false;
	next_state.can_build = true;

	return next_state;
}

// --------------------------
// Functions for action BUILD
// --------------------------
vector<Action> State::buildable_cells(string player) {
	vector<Action> buildable;

	if (player != this->active_player or not this->has_moved or this->has_built) {
		return buildable;
	}

	if(this->moved_worker != "") {
		Worker worker = this->workers.at(player).at(this->moved_worker);

		for (int i = worker.get_coordinates().row - 1; i <= worker.get_coordinates().row + 1; i++) {
			for (int j = worker.get_coordinates().column - 1; j <= worker.get_coordinates().column + 1; j++) {
				if (i >= 0 and i < 5 and j >= 0 and j < 5
					and (i != worker.get_coordinates().row or j != worker.get_coordinates().column)
					and not this->board[i][j].has_worker()
					and this->board[i][j].get_top_level() < 4) {
					buildable.push_back(Action(ActionType::BUILD, worker.get_coordinates(), Coordinates(i, j),
						this->board[i][j].get_top_level() + 1));
				}
			}
		}
	}

	return buildable;
}

State State::build(Coordinates src, Coordinates dst, int level) {
	State next_state = State(this);

	next_state.board[dst.row][dst.column].add_level(level);

	next_state.has_built = true;
	next_state.can_build = false;

	return next_state;
}

// -------------------------
// Functions for action PASS
// -------------------------

// Checks if the agent can pass
bool State::can_pass() {
	return can_pass("SantorinAI");
}

// Checks if the given player can pass
bool State::can_pass(string player) {
	return this->active_player == player && this->has_moved && this->has_built;
}

State State::pass() {
	State next_state = State(this);

	next_state.can_move = true;
	next_state.can_build = false;
	next_state.has_moved = false;
	next_state.has_built = false;

	next_state.moved_worker = "";

	next_state.active_player = this->waiting_player;
	next_state.waiting_player = this->active_player;

	return next_state;
}

void State::print_board()
{
	Block* block;
	for (int i = 0; i < 5; i++) {
		for (int j = 0; j < 5; j++) {
			block = &this->board[i][j];
			if (block->has_worker())
				if (block->get_worker_owner() == "SantorinAI")
					cout << CYAN;
				else
					cout << YELLOW;
			cout << block->get_top_level() << END << " ";
		}
		cout << endl;
	}
}

int State::hash() {
	return 0; // (this->time + 1);
}

bool State::operator==(State* other) {
	// Check for null 
	if (other == nullptr) {
		return false;
	}

	// Check for active player
	/*if (this->active_player != other->active_player) {
		cout << YELLOW << "Different active player" << END << endl;
		return false;
	}*/

	// Check for workers

	// The states have the same number of players with workers
	if (this->workers.size() != other->workers.size()) {
		cout << YELLOW << "Different worker size" << END << endl;
		return false;
	}

	// Cycling over the players with workers
	for (const auto& workers_elem : this->workers) {
		string player = workers_elem.first;
		map<string, Worker> worker_list = workers_elem.second;

		// The player has the same number of workers in both states
		if (this->workers[player].size() != other->workers[player].size()) {
			cout << YELLOW << "Different worker " << player << " size" << END << endl;
			return false;
		}

		// The player's workers are in the same position in both states
		for (const auto& worker_tuple : worker_list) {
			string worker_id = worker_tuple.first;
			
			if (this->workers[player][worker_id].get_coordinates() != other->workers[player][worker_id].get_coordinates()) {
				cout << YELLOW << "Different worker position " << player << " " << worker_id << END << endl;
				return false;
			}
		}
	}

	// Check for board - takes into account reduction
	for (int i = 0; i < 5; i++) {
		for (int j = 0; j < 5; j++) {
			// No check for workers, already done
			if (this->board[i][j].get_top_level() != other->board[i][j].get_top_level()) {
				cout << YELLOW << "Different block " << i << ":" << j << END << endl;
				return false;
			}
		}
	}

	cout << YELLOW << "SAME STATE" << END << endl;
	return true;
}
