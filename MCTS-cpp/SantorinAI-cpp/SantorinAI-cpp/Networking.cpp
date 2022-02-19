#include <iostream>
#include <winsock.h>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>

#include "Networking.h"
#include "Colors.h"

using namespace std;

SOCKET Networking::sock;
bool Networking::keep_alive;
queue<string> Networking::messageQ;

mutex Networking::queue_mtx;
condition_variable Networking::queue_wait;

unique_lock<mutex> Networking::lck(Networking::queue_mtx);

Networking::Networking() {
}

bool Networking::open_connection(const char* host, int port) {
    // Winsock element
    WSADATA wsadata;

    // Error checks for winsock
    int error = WSAStartup(0x0202, &wsadata);
    if (error) {
        print_error("Winsock error " + error);
        return false;
    }
    if (wsadata.wVersion != 0x0202)
    {
        print_error("Wrong version");
        WSACleanup();
        return false;
    }

    // Socket initialization

    // Socket address
    SOCKADDR_IN target;

    target.sin_family = AF_INET; // IPv4
    target.sin_port = htons(port);
    target.sin_addr.s_addr = inet_addr(host);

    // Socket creation and error check
    this->sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (this->sock == INVALID_SOCKET)
    {
        print_error("Cannot create socket");
        return false;
    }

    // Connection
    if (connect(this->sock, (SOCKADDR*)&target, sizeof(target)) == SOCKET_ERROR)
    {
        print_error("Server unavailable");
        return false;
    }

    Networking::keep_alive = true;
       
    this->t_reader = thread(&Networking::message_reader, Networking());
    this->t_ping = thread(&Networking::pinger, Networking());

    return true;
}

void Networking::close_connection() {
    Networking::keep_alive = false;

    this->t_ping.join();
    this->t_reader.join();

    if(this->sock)
        closesocket(this->sock);

    this->sock = NULL;

    WSACleanup();
}

bool Networking::is_alive() {
    return Networking::keep_alive;
}

void Networking::print_error(const char* msg) {
    cout << RED << msg << ". Terminating." << END << endl;
}

bool Networking::send_msg(string msg) {
    return send_msg(msg, false);
}

bool Networking::send_msg(string msg, bool verbose) {
    int len = msg.length();
    msg = msg + '\n';
    return send_msg(msg.c_str(), len + 1, verbose);
}

bool Networking::send_msg(const char* msg, int len, bool verbose) {
    int sent = send(this->sock, msg, len, 0);

    if(verbose)
        cout << CYAN << "Sent " << sent << "/" << len << " bytes: " << msg << END;
    
    if (sent != len) { // if sent is -1 the method failed
        this->keep_alive = false;
        this->queue_wait.notify_all();
        return false;
    }

    return true;
}

void Networking::pinger() {
    cout << GREEN << "Pinger starting." << END << endl;

    while (Networking::keep_alive) {
        if (!send_msg("{\"type\":\"PING\",\"message\":\"{\\\"message\\\":\\\"AIping\\\"}\"}")) {
            print_error("Pinger error");
            Networking::keep_alive = false;
            this->queue_wait.notify_all();
            return;
        }
        this_thread::sleep_for(chrono::milliseconds(500));
    }

    cout << GREEN << "Pinger terminated correctly." << END << endl;
}

void Networking::message_reader() {
    cout << GREEN << "Message reader starting." << END << endl;
    char buff[1001];
    char* message;
    int read;
    int i;
    int k;
    int len;

    while (Networking::keep_alive) {
        read = recv(this->sock, buff, 1000, 0);
        if (read == -1) {
            print_error("Message reader error");
            Networking::keep_alive = false;
            this->queue_wait.notify_all();
            return;
        }
        buff[read] = '\0';

        len = 0;
        i = 0;
        do {
            // Discards characters before JSON start
            message = NULL;
            while (i < read) {
                if (buff[i] == '{' and buff[i + 1] == '\"') {
                    message = buff + i;
                    break;
                }                
                i++;
            }

            if (message != NULL) {                
                len = strlen(message);

                // Due to standard JSON messages the offset to the type is known
                if (!(message[9] == 'P'
                    && message[10] == 'I'
                    && message[11] == 'N'
                    && message[12] == 'G')) {

                    // Discards characters after json end
                    k = len - 1;
                    while (message[k] != '}') {
                        message[k] = '\0';
                        k--;
                    }

                    // Enqueues the message and notifies the reader
                    this->messageQ.push(string(message));
                    this->queue_wait.notify_all();
                }
                i += len;                
            }
        } while (i < read);
    }

    cout << GREEN << "Message reader terminated correctly." << END << endl;
}

string Networking::get_message() {
    while (this->messageQ.empty() and Networking::keep_alive) 
        this->queue_wait.wait(this->lck);

    if (!Networking::keep_alive)
        return string();

    string ret = this->messageQ.front();
    this->messageQ.pop();
    return ret;
}
