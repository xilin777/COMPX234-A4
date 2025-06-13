import sys
import socket

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