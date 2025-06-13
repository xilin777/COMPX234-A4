import sys

# Parse command line arguments
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python UDPclient.py <hostname> <port> <files.txt>")
        sys.exit(1)
    
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    file_list = sys.argv[3]
    print(f"Client configured to connect to {hostname}:{port} with file list {file_list}")