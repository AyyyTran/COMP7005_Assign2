import socket
import sys

BUFFER_SIZE = 4096

def count_alphabetic_chars(file_data):
    return sum(c.isalpha() for c in file_data)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error retrieving local IP address: {e}")
        return "Unable to retrieve local IP."

def validate_port(port):
    if not (1024 <= port <= 65535):
        print(f"Invalid port number: {port}. Port must be between 1024 and 65535.")
        sys.exit(1)

def create_server_socket(port):
    validate_port(port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('0.0.0.0', port))
    except OSError as e:
        if e.errno == 98:
            print(f"Error: Port {port} is already in use. Please use a different port or stop the running server.")
        else:
            print(f"Unexpected error: {e}")
        return None
    server_socket.listen(5)
    server_socket.settimeout(1)  
    print(f"Server is listening on port {port}...")
    return server_socket

def accept_client_connection(server_socket):
    try:
        client_socket, client_address = server_socket.accept()
        print(f"Client connected ...")
        return client_socket
    except socket.timeout:
        return None  
    except KeyboardInterrupt:
        print("\nServer shutting down while waiting for a connection.")
        server_socket.close()
        sys.exit(0)

def receive_file_from_client(client_socket):
    file_data = b""
    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            file_data += data
    except KeyboardInterrupt:
        print("\nTransfer interrupted by server. Closing connection.")
        client_socket.close()
        sys.exit(0)
    except socket.error as e:
        print(f"Socket error during file transfer: {e}")
    return file_data

def send_response_to_client(client_socket, response):
    try:
        client_socket.sendall(response.encode())
    except socket.error as e:
        print(f"Error sending response to client: {e}")

def handle_client(client_socket):
    try:
        file_data = receive_file_from_client(client_socket)
        try:
            file_text = file_data.decode()
        except UnicodeDecodeError as e:
            print(f"Error decoding file data: {e}")
            return
        letter_count = count_alphabetic_chars(file_text)
        response = f"Alphabetic character count: {letter_count}"
        send_response_to_client(client_socket, response)
        print(f"Processed file: counted {letter_count} alphabetic characters.")
    except KeyboardInterrupt:
        print("\nServer interrupted while processing client. Shutting down.")
        sys.exit(0)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()
        print(f"Client disconeccted.")

def start_server(port):
    local_ip = get_local_ip()
    print(f"Server IP address: {local_ip}")
    
    server_socket = create_server_socket(port)
    if server_socket is None:
        sys.exit(1)
    
    try:
        while True:
            try:
                client_socket = accept_client_connection(server_socket)
                if client_socket:
                    handle_client(client_socket)
            except KeyboardInterrupt:
                print("\nServer shutting down.")
                break
    except KeyboardInterrupt:
        print("\nServer interrupted (Ctrl+C). Shutting down...")
    finally:
        if server_socket:
            server_socket.close()
            print("Server socket closed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='TCP server for receiving and processing file content.')
    parser.add_argument('--port', type=int, required=True, help='Port number for the server to listen on')

    args = parser.parse_args()

    start_server(args.port)
