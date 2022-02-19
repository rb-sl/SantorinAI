#pragma once

#include <iostream>
#include <winsock.h>
#include <chrono>
#include <thread>
#include <queue>
#include <mutex>
#include <condition_variable>

class Networking
{
private:
	static SOCKET sock;
	static bool keep_alive;
	std::thread t_ping;
	std::thread t_reader;
	static std::queue<std::string> messageQ;
	static std::mutex queue_mtx;
	static std::condition_variable queue_wait;
	static std::unique_lock<std::mutex> lck;

	void print_error(const char* msg);
	void pinger();
	void message_reader();

public:
	Networking();
	bool is_alive();
	bool open_connection(const char* host, int port);
	void close_connection();
	bool send_msg(std::string msg);
	bool send_msg(std::string msg, bool verbose);
	bool send_msg(const char* msg, int len, bool verbose);	
	std::string get_message();
};
