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
        
        file_size = os.path.getsize(filename)
        server_socket.sendto(f"OK {filename} SIZE {file_size} PORT {port}".encode(), client_address)
        print(f"[TRANSFER] Starting {filename} ({file_size} bytes) on port {port}")
        
        # Open file for reading in binary mode
        with open(filename, 'rb') as f:
            while True:
                try:
                    data, addr = client_socket.recvfrom(2048)
                    request = data.decode().strip()

                    if request.startswith(f"FILE {filename} GET"):
                        parts = request.split()
                        start = int(parts[4])
                        end = int(parts[6])
                        f.seek(start)
                        chunk = f.read(end - start + 1)

                        if not chunk:  
                            break

                        encoded = base64.b64encode(chunk).decode('utf-8')
                        if not encoded:
                            print("[ERROR] Base64 encoding failed!")
                            continue

                        response = f"FILE {filename} OK START {start} END {end} DATA {encoded}"
                        client_socket.sendto(response.encode(), addr)
                        print(f"[SENT] Block {start}-{end} ({len(chunk)} bytes)")

                    elif request.startswith(f"FILE {filename} CLOSE"):
                        client_socket.sendto(f"FILE {filename} CLOSE_OK".encode(), addr)
                        break

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[ERROR] Processing error: {str(e)}")
                    break

    

if __name__ == "__main__":
    import sys
    
    
    main( )