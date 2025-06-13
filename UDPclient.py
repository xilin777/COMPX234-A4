import sys
import socket

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