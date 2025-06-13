import sys

# Parse command line arguments
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python UDPserver.py <port>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    print(f"Server configured to listen on port {port}")