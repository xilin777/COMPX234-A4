import sys
import socket
import threading
import random
import os
import base64
# Handle file transmission in a separate thread
def handle_file_transmission(filename, client_addr, welcome_sock):
    # Select a random port
    data_port = random.randint(50000, 51000)
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_sock.bind(('', data_port))

    # Check if file exists
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        response = f"OK {filename} SIZE {size} PORT {data_port}"
    else:
        response = f"ERR {filename} NOT_FOUND"
    welcome_sock.sendto(response.encode(), client_addr)

    if os.path.exists(filename):
        with open(filename, "rb") as f:
            while True:
                request, addr = data_sock.recvfrom(4096)
                request = request.decode().strip()
                parts = request.split()
                if parts[0] == "FILE" and parts[3] == "CLOSE":
                    data_sock.sendto(f"FILE {filename} CLOSE_OK".encode(), addr)
                    break
                elif parts[0] == "FILE" and parts[3] == "GET":
                    start = int(parts[5])
                    end = int(parts[7])
                    f.seek(start)
                    data = f.read(end - start + 1)
                    encoded_data = base64.b64encode(data).decode()
                    response = f"FILE {filename} OK START {start} END {end} DATA {encoded_data}"
                    data_sock.sendto(response.encode(), addr)
        data_sock.close()


# Parse command line arguments
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python UDPserver.py <port>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    print(f"Server configured to listen on port {port}")
    
    # Create UDP socket and bind
    welcome_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    welcome_sock.bind(('', port))

    print(f"Server listening on port {port}")
    while True:
        request, client_addr = welcome_sock.recvfrom(4096)
        print(f"Received request from {client_addr}: {request.decode().strip()}")