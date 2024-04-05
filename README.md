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
