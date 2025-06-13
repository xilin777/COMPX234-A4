import sys
import socket
import time

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
    except FileNotFoundError:
        print(f"Error: {file_list} not found.")
        sock.close()
        sys.exit(1)

    sock.close()