#define _POSIX_C_SOURCE 200809L
#define BUFF_SIZE 65536
#define SERVER_PORT 2020
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <ctype.h> 

// Struktura która będzie zwracac handleRequest
typedef struct{
    unsigned int first;
    unsigned int second;
}Pair;

// Stany do automatu obsługującego zapytania
enum State {
    START,
    ERROR,
    SPACE,
    LETTER
};

bool isPalindrome(unsigned char* begin, unsigned char* end);

// Zwraca Pair(liczba_palindromow, liczba_słów)
// Większa liczba palindromow niz calkowita liczba slowa oznacza ERROR
Pair handleRequest(unsigned char* buff, unsigned int length);

int main(int argc, char * argv[])
{
    int server_sock;   // gniazdko servera
    socklen_t addr_len;
    ssize_t cnt;    // wyniki zwracane przez read() i write() są tego typu
    bool add_newline = false; // dodaje znak nowej linii

    struct sockaddr_in client_addr; // gniazdo klienta

    server_sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (server_sock == -1) {
        perror("socket error");
        return EXIT_FAILURE;
    }

    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_addr = { .s_addr = htonl(INADDR_ANY) }, // Long Host to network byte order
        .sin_port = htons(SERVER_PORT)
    };

    if (bind(server_sock, (struct sockaddr *) & addr, sizeof(addr)) == -1) {
        perror("bind error");
        return EXIT_FAILURE;
    }

    memset((char *)& client_addr, 0, sizeof(client_addr));

    addr_len = sizeof(client_addr);

    printf("Server running on port 2020\n");

    bool keep_on_handling_clients = true;

    while (keep_on_handling_clients) {

        unsigned char buff[BUFF_SIZE];
        Pair result;
        unsigned int message_length;
    
        cnt = recvfrom(server_sock, buff, BUFF_SIZE, 0, (struct sockaddr *)&client_addr, &addr_len);
        if (cnt == -1) {
            perror("recvfrom error");
            exit(EXIT_FAILURE);
        }

        add_newline = false;

        if(cnt == 0){ // Pusta wiadomość
            result.first = 0;
            result.second = 0;
        }else if (*(buff + cnt -1) == '\n'){ // Czy dodac \r\n do odpowiedzi
            add_newline = true;
            --cnt;
            if(*(buff + cnt -1) == '\r'){
                --cnt;
            }
        }
        // Poprzez odejmowanie od cnt przy \r i \r\n nie beda one sprawdzane przez handleRequest

        if(cnt != 0){ // Zapytanie nie jest puste
            result = handleRequest(buff, cnt);
        }else{ // Zapytanie to było samo \r lub \r\n
            result.first = 0;
            result.second = 0;
        }

        if(result.first > result.second){ // ERROR
            if(add_newline){
                memcpy(buff, "ERROR\r\n", 7);
                message_length = 7;
            }else{
                memcpy(buff, "ERROR", 5);
                message_length = 5;
            }

            printf("Received invalid message...\n");
        }else{
            if(add_newline){
                message_length = snprintf((char*)buff, BUFF_SIZE, "%u/%u\r\n", result.first, result.second);
            }else{
                message_length = snprintf((char*)buff, BUFF_SIZE,"%u/%u", result.first, result.second);
            }
        }

        cnt = sendto(server_sock, buff, message_length, 0, (struct sockaddr *)&client_addr, addr_len);
        if (cnt == -1) {
            perror("write error");
            return EXIT_FAILURE;
        }

        printf("wrote %zi bytes\n", cnt);
    }

    if (close(server_sock) == -1) {
        perror("server close error");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

bool isPalindrome(unsigned char* begin, unsigned char* end)
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

Pair handleRequest(unsigned char* buff, unsigned int length)
{
    unsigned char* start = buff; // Początek słowa
    unsigned char* end = buff; // Koniec słowa
    int palindromeNum = 0, totalNum = 0;
    enum State state = START;
    Pair result;

    // Handle Start state
    if ((*end >= 65 && *end <= 90) ||  (*end >= 97 && *end <= 122)) // Duże lub małe litery
    {
        state = LETTER;
        ++end;
    }else{
        state = ERROR;
    }

    while(end != buff + length  && state != ERROR )
    {
        if ((*end >= 65 && *end <= 90) ||  (*end >= 97 && *end <= 122)){ // Duże i małe litery
            ++end;
            state = LETTER;
        }else if(*end == 32){ // spacja
            if(state == LETTER){ // Koniec słowa
                ++totalNum;
                if(isPalindrome(start, end-1)){
                    ++palindromeNum;
                }
                state = SPACE;
                ++end;
                start = end;
            }else if(state == SPACE){ // Wielokrotna spacja -> Błąd
                state = ERROR;
            }
        }else{
            state = ERROR;
        }
    }

    if(state == ERROR || state == SPACE){ // Bład lub spacja na koncu
        result.first = 2;
        result.second = 1;
    }else{

        // Sprawdzanie ostatniego słowa w zapytaniu (Głowna petla sprawdza tylko przy spacji a na koncu zapytania nie może ona wystąpic)
        if(isPalindrome(start, end-1)){
            ++palindromeNum;
        }
        ++totalNum;

        result.first = palindromeNum;
        result.second = totalNum;
    }
    return result;
}