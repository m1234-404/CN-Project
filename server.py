import socket
import ssl
import threading
import queue

HOST = "0.0.0.0"
PORT = 5000

USERNAME = "user1"
PASSWORD = "pass123"

clients = []
client_queues = {}

# SSL setup
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(" Secure Server Started...")
print("Waiting for clients...\n")

COMMANDS_INFO = (
    "\n Available Commands:\n"
    "  TURN_ON_LIGHT     - Turn the light ON\n"
    "  TURN_OFF_LIGHT    - Turn the light OFF\n"
    "  GET_STATUS        - Get device status\n"
    "  GET_TEMPERATURE   - Get current temperature\n"
    "  GET_DEVICE_CONFIG - Get client device configuration\n"
    "  EXIT              - Disconnect\n"
)


def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    try:
        # Authentication
        username = conn.recv(4096).decode()
        password = conn.recv(4096).decode()

        if username == USERNAME and password == PASSWORD:
            conn.send("AUTH_SUCCESS".encode())
            clients.append(conn)
            client_queues[conn] = queue.Queue()
            print(f" Authenticated: {addr}")

            # Send available commands after auth
            conn.send(COMMANDS_INFO.encode())
        else:
            conn.send("AUTH_FAILED".encode())
            print(f" Authentication failed: {addr}")
            conn.close()
            return

        # Only this thread ever calls recv() on this socket
        while True:
            msg = conn.recv(4096).decode()

            if not msg:
                break

            print(f"\n From {addr}: {msg}")

            if msg.startswith("CLIENT:"):
                actual = msg[len("CLIENT:"):]

                if actual == "TURN_ON_LIGHT":
                    response = "Server: Light turned ON"
                elif actual == "TURN_OFF_LIGHT":
                    response = "Server: Light turned OFF"
                elif actual == "GET_STATUS":
                    response = "Server Status: ACTIVE"
                elif actual == "GET_TEMPERATURE":
                    response = "Server Temp: 30 C"
                elif actual == "GET_DEVICE_CONFIG":
                    response = "Server: GET_DEVICE_CONFIG not applicable on server side"
                elif actual == "EXIT":
                    conn.send("Disconnecting...".encode())
                    break
                else:
                    response = " Unknown command. Type a valid command."

                conn.send(response.encode())

            else:
                # Response to a server-issued command — route to queue
                if conn in client_queues:
                    client_queues[conn].put(msg)

    except Exception as e:
        print(f"Error with client {addr}: {e}")

    finally:
        if conn in clients:
            clients.remove(conn)
        client_queues.pop(conn, None)
        conn.close()
        print(f"Client disconnected: {addr}")


def accept_clients():
    while True:
        try:
            client_socket, addr = server_socket.accept()
            secure_conn = context.wrap_socket(client_socket, server_side=True)
            threading.Thread(target=handle_client, args=(secure_conn, addr), daemon=True).start()
        except Exception as e:
            print(f"Error accepting client: {e}")


def server_commands():
    print("  Server control ready. Type a command to send to all clients.\n")
    while True:
        try:
            command = input("\n  Server Command: ").strip()

            if not command:
                continue

            if not clients:
                print("  No clients connected.")
                if command == "EXIT":
                    print("Shutting down server...")
                    break
                continue

            for c in list(clients):
                try:
                    c.send(command.encode())
                    response = client_queues[c].get(timeout=10)
                    print(f"\n Client Response:\n{response}")
                except queue.Empty:
                    print("  No response from client (timeout)")
                except Exception as e:
                    print(f"Error sending command: {e}")

            if command == "EXIT":
                print("Shutting down server...")
                break

        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break


threading.Thread(target=accept_clients, daemon=True).start()
server_commands()
server_socket.close()
