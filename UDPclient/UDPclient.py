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
def download_file(sock, server_addr, filename):
    # Send DOWNLOAD request
    request = f"DOWNLOAD {filename}"
    response = send_and_receive(sock, server_addr, request)
    if not response:
        return False

    # Parse response
    parts = response.split()
    if parts[0] == "ERR":
        print(f"Error: File {filename} not found on server.")
        return True
    elif parts[0] == "OK":
        size = int(parts[3])
        port = int(parts[5])
        server_addr = (server_addr[0], port)
        print(f"Downloading {filename}, size: {size} bytes")

        # Create local file
        with open(filename, "wb") as f:
            downloaded = 0
            while downloaded < size:
                start = downloaded
                end = min(start + 999, size - 1)  # Request 1000 bytes at a time
                request = f"FILE {filename} GET START {start} END {end}"
                response = send_and_receive(sock, server_addr, request)
                if not response:
                    break
                parts = response.split(" DATA ")
                if parts[0] == f"FILE {filename} OK START {start} END {end}":
                    data = base64.b64decode(parts[1])
                    f.seek(start)
                    f.write(data)
                    downloaded += len(data)
                    print("*", end="", flush=True)
            print("\nFile download complete.")

        # Send close request
        request = f"FILE {filename} CLOSE"
        response = send_and_receive(sock, server_addr, request)
        if response and response == f"FILE {filename} CLOSE_OK":
            print(f"Closed connection for {filename}")
        return True
    return False

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