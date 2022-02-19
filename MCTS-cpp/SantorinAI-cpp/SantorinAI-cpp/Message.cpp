#include <iostream>
#include <regex>
#include <nlohmann/json.hpp>

#include "Message.h"
#include "Coordinates.h"

using json = nlohmann::json;

using namespace std;

// Envelope
void to_json(json& j, const envelope& m) {
    j = json{ {"type", m.type}, {"message", m.message} };
}
void from_json(const json& j, envelope& m) {
    j.at("type").get_to(m.type);
    j.at("message").get_to(m.message);
}

// Server State
void to_json(json& j, const serverstate& m) {
    j = json{ {"open", m.open}, {"active", m.active} };
}
void from_json(const json& j, serverstate& m) {
    j.at("open").get_to(m.open);
    j.at("active").get_to(m.active);
}

// Players message
void to_json(json& j, const players& m) {
    j = json{ {"players", m.player_map}, {"player", m.active_player} };
}
void from_json(const json& j, players& m) {
    j.at("players").get_to(m.player_map);
    j.at("player").get_to(m.active_player);
}

// Update message
void to_json(json& j, const update& m) {
    j = json{ {"boardUpdate", m.board_update},
        {"reachableCells", m.reachable_cells}, 
        {"buildableCells", m.buildable_cells}, 
        {"canPlaceWorker", m.can_place}, 
        {"canPass", m.can_pass}, 
        {"canUndo", m.can_undo}, 
        {"player", m.player} };
}
void from_json(const json& j, update& m) {
    try {
        j.at("boardUpdate").get_to(m.board_update);
    }
    catch (nlohmann::detail::type_error e) {
        cout << "Board not found: " << e.what() << endl;
    }
    try {
        j.at("reachableCells").get_to(m.reachable_cells);
    }
    catch (nlohmann::detail::type_error e) {
        cout << "Reachable cells not found: " << e.what() << endl;
    }
    try {
        j.at("buildableCells").get_to(m.buildable_cells);
    }
    catch(nlohmann::detail::type_error e) {
        cout << "Buildable cells not found: " << e.what() << endl;
    }
    j.at("canPlaceWorker").get_to(m.can_place);
    j.at("canUndo").get_to(m.can_undo);
    j.at("canPass").get_to(m.can_pass);
    j.at("player").get_to(m.player);
}

// Endgame message
void to_json(json& j, const endgame& m) {
    j = json{ {"isWinner", m.is_winner}, {"player", m.player} };
}
void from_json(const json& j, endgame& m) {
    j.at("isWinner").get_to(m.is_winner);
    j.at("player").get_to(m.player);
}

// Coordinates object
void to_json(json& j, const coord& c) {
    j = json{ {"row", c.row}, {"column", c.column} };
}
void from_json(const json& j, coord& c) {
    j.at("row").get_to(c.row);
    j.at("column").get_to(c.column);
}

// Block object
void to_json(json& j, const block& c) {
    j = json{ {"levelList", c.level_list}, {"workerOwner", c.worker_owner}, {"workerSex", c.worker_id}};
}
void from_json(const json& j, block& c) {
    j.at("levelList").get_to(c.level_list);
    // Using defaults
    c.worker_owner = j.value("workerOwner", "");
    c.worker_id = j.value("workerSex", "");
}

bool coord::operator<(const coord& rhs) const {
    return this->row * 5 + this->column < rhs.row * 5 + rhs.column;
}
