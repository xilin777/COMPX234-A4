import sys
import socket
import time
import base64

def send_and_receive(sock, message, server_address, timeout=2, max_retries=3):
    for attempt in range(max_retries):
        try:
            sock.sendto(message.encode(), server_address)
            sock.settimeout(timeout * (attempt + 1))
            response, _ = sock.recvfrom(4096)
            return response.decode().strip()
        except socket.timeout:
            print(f"[RETRY] Timeout (attempt {attempt + 1})")
        except Exception as e:
            print(f"[ERROR] Communication error: {str(e)}")
            break
    return None

# Download single file
def download_file(control_sock, filename, server_address):
    # File metadata request
    response = send_and_receive(control_sock, f"DOWNLOAD {filename}", server_address)
    if not response:
        print(f"[FAILED] No response for {filename}")
        return False

    if response.startswith("ERR"):
        print(f"[ERROR] Server response: {response}")
        return False 

        parts = response.split()
    file_size = int(parts[3])
    data_port = int(parts[5])
    data_address = (server_address[0], data_port)
    print(f"[INFO] Downloading {filename} ({file_size} bytes) via port {data_port}")
        
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as data_sock:
        data_sock.settimeout(5)

        try:
            with open(filename, 'wb') as f:
                downloaded = 0
                while downloaded < file_size:
                    # Block request
                    start = downloaded
                    end = min(start + 999, file_size - 1)
                    request = f"FILE {filename} GET START {start} END {end}"
                    response = send_and_receive(data_sock, request, data_address)
                    if not response:
                        print("[ERROR] No data response")
                        continue

                    if " DATA " not in response:
                        print(f"[ERROR] Invalid response format: {response[:50]}...")
                        continue

                    header, payload = response.split(" DATA ", 1)
                    expected_header = f"FILE {filename} OK START {start} END {end}"
                    if header != expected_header:
                        print(f"[ERROR] Header mismatch: expected {expected_header}, got {header}")
                        continue 
                    
# Reliable send and receive function
def send_and_receive(sock, server_addr, message, max_attempts=5, initial_timeout=1):
    attempts = 0
    current_timeout = initial_timeout
    while attempts < max_attempts:
        try:
            # Send request
            sock.sendto(message.encode(), server_addr)
            # Set timeout
            sock.settimeout(current_timeout)
            # Receive response
            response, _ = sock.recvfrom(4096)
            return response.decode().strip()
        except socket.timeout:
            print(f"Timeout, attempt {attempts + 1}, doubling timeout to {current_timeout * 2}s")
            attempts += 1
            current_timeout *= 2
            time.sleep(current_timeout)  # Wait before retrying
    print("Max attempts reached, giving up.")
    return None

# Parse command line arguments
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python UDPclient.py <hostname> <port> <files.txt>")
        sys.exit(1)
    
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    file_list = sys.argv[3]
    print(f"Client configured to connect to {hostname}:{port} with file list {file_list}")

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Read file list
    try:
        with open(file_list, "r") as f:
            filenames = [line.strip() for line in f if line.strip()]
            print(f"Files to download: {filenames}")
            for filename in filenames:
                download_file(sock, (hostname, port), filename)
    except FileNotFoundError:
        print(f"Error: {file_list} not found.")
        sock.close()
        sys.exit(1)

    sock.close()