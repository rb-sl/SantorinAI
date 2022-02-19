#include "Node.h"

#include <map>

using namespace std;

Node::Node(State s) : Node(s, nullptr, "NONE", "") {}

Node::Node(State s, Node* parent, string action, string message) : state(s) {
	this->parent = parent;
	this->action = action;
	this->message = message;

	this->n_wins = 0;
	this->n_sims = 0;
	this->ucb1 = INFINITY;
}

State* Node::get_state()
{
	return &(this->state);
}

void Node::set_parent(Node* parent) {
	this->parent = parent;
}

Node* Node::get_parent() {
	return this->parent;
}

bool Node::has_children() {
	return not this->children.empty();
}

vector<Node*> Node::get_children() {
	return this->children;
}

Node* Node::add_child(State* state, string action, string message) {
	Node* new_node = new Node(state, this, action, message);
	this->children.push_back(new_node);
	return new_node;
}

//Node* Node::node_update(map<coord, block> board_update, string player)
//{
//	State new_state = State(this->state);
//	new_state.set_active_player(player);
//	
//	for (const auto& tuple : board_update) {
//		coord c = tuple.first;
//		block to_update = tuple.second;
//
//		new_state.update_board(c, to_update);
//	}
//	new_state.print_board();
//
//	// Case of undo
//	if (new_state == this->parent->get_state())
//		return this->parent;
//
//	if (!this->children.empty()) {
//		// If children were expanded returns the right child
//		for (const auto& child : this->children)
//			if (new_state == &child->state)
//				return child;
//	}
//	else {
//		return add_child(&new_state, "UPDATE", "");
//	}
//
//	return this;
//}

float Node::get_ucb1() {
	return this->ucb1;
}

void Node::update_ucb1() {
	int parent_sim = this->parent != nullptr ? this->parent->n_sims : 1;
	this->ucb1 = this->n_wins / this->n_sims + ALPHA * sqrt(log(parent_sim) / this->n_sims);
}

void Node::print_tree(int n_tabs) {
	for (int i = 0; i < n_tabs; i++) {
		cout << "\t";
	}
	cout << this->state.get_active_player() << " " << this->action << endl;
	for (auto child : this->children) {
		child->print_tree(n_tabs + 1);
	}
}

