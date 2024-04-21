#define BUFF_SIZE 1024
#define PORT 2020
#define LINE_TERMINATOR "\r\n"
#define MAX_CLIENTS_NUMBER 20
#define MAX_WAIT_TIME_SECONDS 60 * 10 

#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <cstring>
#include <thread>
#include <sys/time.h>

using namespace std;

void logError(int val, string message){
    if(val == -1){
        cerr << message << "\n";
        exit(EXIT_FAILURE);
    }
}

class ClientHandler{
    private:
        enum resultState{
            FINISHED_REQUEST, UNFINISHED_REQUEST, UNFINISHED_REQUEST_ERROR, FINISHED_REQUEST_ERROR
        };

        enum requestState{
            START, ERROR, LETTER, SPACE
        };

        unsigned int total_words;
        unsigned int total_palindroms;
        int client_socket;
        char* buff;

        resultState request_result_state;
        requestState request_state;

        bool isPalindrome(char* begin, char* end);

        // Obsługuje żądanie do \r\n i zwraca wskaźnika na koniec zapytania (\n)
        char* handleRequest(char* begin, int request_len);

        void sendRespond(bool error=false);

    public:
        ClientHandler(int socket) : 
        total_words{0}, total_palindroms{0}, request_result_state{FINISHED_REQUEST}, request_state{START}{
            buff = new char[BUFF_SIZE];
            client_socket = socket;
        };

        ~ClientHandler(){
            if(close(this->client_socket) == -1){
                cerr << "Close Client Socket Error\n";
            }
            delete buff;
        };

        void handleClient(); 
};

int main()
{
    int listen_socket;
    int client_socket;
    bool handling_clients=true;

    listen_socket = socket(AF_INET, SOCK_STREAM, 0);
    logError(listen_socket, "create socket error");

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(PORT);

    struct timeval timeout;
    timeout.tv_sec = MAX_WAIT_TIME_SECONDS;
    timeout.tv_usec = 0;

    logError(bind(listen_socket, (struct sockaddr *) & addr, sizeof(addr)), "bind socket error");

    logError(listen(listen_socket, MAX_CLIENTS_NUMBER), "listen error");

    std::cout << "Server running on port: " << PORT << "\n";

    while(handling_clients)
    {
        
        client_socket = accept(listen_socket, NULL, NULL);
        logError(client_socket, "accept error");

        logError(setsockopt(client_socket, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout)), "Setsockopt error");

        cout << "Connected with client: " << client_socket << "\nStarting new thread...\n";

        unique_ptr<ClientHandler> handler(new ClientHandler(client_socket));

        thread handlerThread(&ClientHandler::handleClient, move(handler));
        handlerThread.detach();
        
    }

    logError(close(listen_socket), "close error");
}

bool ClientHandler::isPalindrome(char* begin, char* end)
{
    while(begin <= end)
    {
        if(tolower(*begin) != tolower(*end))
        {
            return false;
        }else{
            ++begin;
            --end;
        }
    }

    return true;
}

char* ClientHandler::handleRequest(char* begin, int request_len)
{
    char* start = begin; // Początek słowa
    char* end = begin; // Koniec słowa

    // Handle Start state
    if(this->request_state == START)
    {
        if ((*end >= 'a' && *end <= 'z') ||  (*end >= 'A' && *end <= 'Z')) // Duże lub małe litery
        {
            this->request_state = LETTER;
            ++end;
        }else{
            this->request_state = ERROR;
        }
    }

    while(this->request_state != ERROR)
    {
        if(end == begin+request_len){ // Koniec danych, brakuje \r\n
            this->request_result_state=UNFINISHED_REQUEST;
            return start;
        }

        if ((*end >= 'a' && *end <= 'z') ||  (*end >= 'A' && *end <= 'Z'))
        {
            this->request_state = LETTER;
            ++end;
        }else if(*end == ' '){
            if(this->request_state == LETTER){ // Koniec słowa
                ++this->total_words;
                if(this->isPalindrome(start, end-1)){
                    ++this->total_palindroms;
                }

                this->request_state = SPACE;
                start = ++end; // za spacją
            }else if(this->request_state == SPACE){ // Wielokrotna spacja -> Błąd
                this->request_state = ERROR;
            }
        }else if(*end == '\r' && *(end+1) == '\n'){ // Koniec pojedynczego zapytania
            if(begin != end && *(end-1) == ' '){ // Spacja na końcu zapytania
                this->request_state = ERROR;
                break;
            }

            ++this->total_words;
            if(isPalindrome(start, end-1)){ // end jest na miejscu \r, więc end-1 to ostatni znak słowa
                ++this->total_palindroms;
            }

            this->request_result_state = FINISHED_REQUEST;
            return ++end; // wskaźnik na \n
        }else{ // Niedozwolony znak
            this->request_state = ERROR;
        }
    }

    if(this->request_state == ERROR){
        while(start != begin+request_len){
            if(*start == '\r' && *(start+1) == '\n'){
                this->request_result_state = FINISHED_REQUEST_ERROR;
                return start+1;
            }
            ++start;
        }
        this->request_result_state = UNFINISHED_REQUEST_ERROR;
        return nullptr;

    }else{ // W tej porcji danych nie było \r\n zwracam wskaźnik na początek przetwarzanego, nieukończonego słowa
        this->request_result_state = UNFINISHED_REQUEST; 
        return start;
    }
}

void ClientHandler::sendRespond(bool error)
{
    int msg_len;
    char temp[20];
    if(error){
        strcpy(temp, "ERROR\r\n");
        msg_len = 7;
    }else{
        msg_len = snprintf(temp, 20, "%u/%u\r\n", this->total_palindroms, this->total_words);
    }

    logError(send(this->client_socket, temp, msg_len, 0), "Send respond Error");

    // Odpowiedź wysłana, można wyzerować
    this->total_palindroms = 0;
    this->total_words = 0;
}

void ClientHandler::handleClient(){
    int count;
    char* begin;
    int unfinished_bytes;
    int bytes_consumed;

    while(true){
        if(this->request_result_state == UNFINISHED_REQUEST){ // Zeby nie nadpisac bajtów z poprzedniej porcji danych
            count = recv(this->client_socket, this->buff+unfinished_bytes, BUFF_SIZE-unfinished_bytes, 0) + unfinished_bytes; // stare bajty + nowe bajty
        }else{
            count = recv(this->client_socket, this->buff, BUFF_SIZE, 0);
        }
    
        if(count  == 0){ // Klienta zakończył połączenie
            cout << "Client " << this->client_socket << " has closed the connection\n";
            break;
        }else if(count == -1){ // Błąd
            cout << "Connection error occured with client: " << this->client_socket << "\n";
            break;
        }

        begin = buff-1;

        // TESTING
        // cout << "\nREAD";
        // for(int i=0; i<count; ++i){
        //     cout << buff[i];
        // }
        // cout << "ENDREAD\n";

        while(count > 0){
            auto end = this->handleRequest(begin+1, count); // +1 z uwagi na to, że handleRequest zwraca wskaźnik na \n

            if(this->request_result_state == UNFINISHED_REQUEST_ERROR)
            {
                // handleRequest radzi sobie z przetwarzaniem zapytania przy stanie ERROR
                break;
            }else if(this->request_result_state == UNFINISHED_REQUEST)
            {
                unfinished_bytes = (begin + count+1) - end; // +1 jak wyżej
                copy(end, end+unfinished_bytes, this->buff); // Kopiuje nieprzetworzone do końca słowo na poczatek bufora
                break;
            }else if(this->request_result_state == FINISHED_REQUEST_ERROR)
            {
                this->sendRespond(true); // ERROR message
                this->request_state=START; // Stan nowego zapytania to początek
                
            }else if(this->request_result_state == FINISHED_REQUEST)
            {     
                this->sendRespond(false);
                this->request_state=START;
            }

            bytes_consumed = end-begin; // Długosć pojedynczego zapytania
            count -= bytes_consumed;
            begin = end;
        }

    }
}
