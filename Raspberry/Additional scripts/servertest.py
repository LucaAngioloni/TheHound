##
## MIT License
## 
## Copyright (c) 2016 Luca Angioloni
## 
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##
import socket
import sys


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('Lucas-MacBook.local', 50001)

print(server_address)

sock.bind(server_address)
sock.listen(1)

print("Listening")


type = "msg"

msg = "ciao come va?"

array = bytearray(type.encode('utf-8'))

array.extend(len(msg).to_bytes(4,'big'))
array.extend(msg.encode('utf-8'))

while True:
    # Wait for a connection
    connection, client_address = sock.accept()

    print("Connected to " + str(client_address))
    try:
        # Receive the data in small chunks and retransmit it
        """
        while True:
            data = connection.recv(16)
            if data:
                connection.sendall(data)
            else:
                break
        """
        connection.sendall(array)
    finally:
        # Clean up the connection
        connection.close()
        print("Connection closed")