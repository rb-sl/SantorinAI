/*
 * SantorinAI project built with C++
 */

#include <iostream>
#include <winsock.h>
#include <nlohmann/json.hpp>


#include "Colors.h"
#include "Networking.h"
#include "Message.h"
#include "AI.h"

#pragma comment(lib, "Ws2_32.lib")

using json = nlohmann::json;
using namespace std;

void delay();

const string NICKNAME = "SantorinAI";
const char* HOST = "127.0.0.1";
const int PORT = 49153;

int main() {
	AI ai(NICKNAME);

	cout << GREEN << NICKNAME << " started." << END << endl
		<< "Connecting to server at " << HOST 
		<< ":" << PORT << "..." << endl;

	Networking net = Networking();
	if (!net.open_connection(HOST, PORT))
		return -1;

	bool keep_playing = true;

	json msg_json;
	while (keep_playing) {
		string msg = net.get_message();
		if (msg.empty())
			break;

		msg_json = json::parse(msg);

		envelope env = msg_json;
		cout << "Processing message " << env.type << ": " << env.message << endl;
		
		msg_json = json::parse(env.message);
		if (env.type == "SERVERSTATE") {
			serverstate ss = msg_json.get<serverstate>();

			// Stops if a game is already going on
			if (!ss.open and ss.active) {
				cout << RED << "Game not available. Terminating." << END << endl;
				break;
			}

			// Sends the initialization message based on the active players
			if (not ss.active) {
				net.send_msg("{\"type\":\"REGISTER\",\"message\":\"{\\\"nickname\\\":\\\"" + NICKNAME + "\\\",\\\"nPlayers\\\":2,\\\"gods\\\":false}\"}");
				cout << CYAN << "Game created, waiting for another player..." << END << endl;
			}
			else {
				net.send_msg("{\"type\":\"REGISTER\",\"message\":\"{\\\"nickname\\\":\\\"" + NICKNAME + "\\\"}\"}");
				cout << CYAN << "Joining game..." << END << endl;
			}
		}
		else if (env.type == "INFO") {
			// Received only on duplicate nickname
			cout << RED << NICKNAME << " is already playing. Terminating." << END << endl;
			break;
		}
		else if (env.type == "PLAYERSMESSAGE") {
			players p = msg_json.get<players>();
			vector<string> player_list;
			for (auto const& key : p.player_map)
				player_list.push_back(key.first);

			// Creates the agent
			ai.set_players(player_list);

			// If it's the active player, chooses the starter
			if (p.active_player == NICKNAME) {
				string starter = ai.choose_starter();
				cout << "Chosen starter: " << starter << endl;
				ai.set_turn(starter);

				delay();
				net.send_msg("{\"type\":\"CHOSESTARTER\",\"message\":\"{\\\"player\\\":\\\""
					+ NICKNAME + "\\\",\\\"starter\\\":\\\"" + starter + "\\\"}\"}");
			}
			else
				cout << "Waiting for the challenger to choose the starting player..." << endl;
		}
		else if (env.type == "UPDATE") {
			update up = msg_json.get<update>();			

			if (!up.board_update.empty())
				//ai.update(up.board_update, up.player);
				ai.server_update(up);
			else
				// On empty board sets the player as active - also at match start
				ai.set_turn(up.player);

			if (up.player == NICKNAME) {
				string message = ai.choose_action();
				delay();
				net.send_msg(message);
			}				
		}
		else if (env.type == "ENDGAME") {
			endgame eg = msg_json.get<endgame>();
			if(!eg.is_winner)
				cout << CYAN << "Game terminated due to " << eg.player << "'s disconnection." << END << endl;
			else
				cout << CYAN << "Game terminated. Winner: " << eg.player << "." << END << endl;
			cout << endl << endl << endl;
		}
	}
	
	net.close_connection();
	return 0;
}

void delay() {
	this_thread::sleep_for(chrono::milliseconds(500));
}
