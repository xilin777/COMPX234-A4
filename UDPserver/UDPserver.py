import sys
import socket
import threading
import random
import os
import base64
# Handle file transmission in a separate thread
def handle_client_request(filename, client_address, server_socket):
    # Send OK message to client
    for attempt in range(3):
        port = random.randint(50000, 51000)
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.bind(('', port))
            print(f"[SUCCESS] Data port {port} bound for {filename}")
            break
        except Exception as e:
            print(f"[WARNING] Port {port} bind failed (attempt {attempt + 1}): {str(e)}")
            client_socket.close()
            if attempt == 2:
                server_socket.sendto(f"ERR {filename} PORT_ERROR".encode(), client_address)
                return

    try:
        # Send OK message to client
        if not (os.path.exists(filename) and os.access(filename, os.R_OK)):
            server_socket.sendto(f"ERR {filename} NOT_FOUND".encode(), client_address)
            return
    except Exception as e:
        print(f"[ERROR] Exception occurred while handling client request: {str(e)}")
        server_socket.sendto(f"ERR {filename} SERVER_ERROR".encode(), client_address)
        return
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
        request = request.decode().strip()
        parts = request.split()
        if parts[0] == "DOWNLOAD" and len(parts) == 2:
            filename = parts[1]
            thread = threading.Thread(target=handle_file_transmission, args=(filename, client_addr, welcome_sock))
            thread.start()
        else:
            print(f"Invalid request from {client_addr}: {request}")