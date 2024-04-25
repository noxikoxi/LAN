# LAN
Programs that use LAN connections

## palindroms-udp

- Udp server written in C
- Calculates number of palindroms words in a request and returns [number_of_palindroms]/[total_words_number].
- Only request with ascii letters + [' ', '\n', '\r'] are accepted.
- Words have to be separated by ' '.
- Space cannot be inserted on the begin or end of a request.
- If request is not accepted server returns "ERROR".
- If request contains "\r\n" or "\n" server adds "\r\n" to response.
- Python script can be used to test server functionality.


## palindroms-tcp

- TCP server written in C++
- Functionality same as UDP server
- Can handle multiple clients at once
- Uses new thread for each client
- Each request must contains "\r\n" as request terminator

## check-website

- simple java program that check if given website is working
- checks response status code and search for given string in html
