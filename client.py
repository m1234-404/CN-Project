import socket
import ssl
import threading
import time
import getpass
import platform
import psutil
import socket as sock

HOST = "192.168.137.128"
PORT = 5000

# SSL setup
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_socket = context.wrap_socket(client_socket, server_hostname=HOST)
secure_socket.connect((HOST, PORT))

print("🔗 Connected to server")

# Ask for credentials
print("🔐 Login Required")
username = input("👤 Username: ")
password = getpass.getpass("🔑 Password: ")

secure_socket.send(username.encode())
secure_socket.send(password.encode())

response = secure_socket.recv(4096).decode()

if response != "AUTH_SUCCESS":
    print("❌ Authentication failed. Wrong username or password.")
    secure_socket.close()
    exit()

print("✅ Device Ready")

commands_info = secure_socket.recv(4096).decode()
print(commands_info)

device_status = "OFF"


def get_device_config():
    """Collect and return device configuration as a formatted string."""
    try:
        ip_address = sock.gethostbyname(sock.gethostname())
    except:
        ip_address = "Unavailable"

    try:
        cpu_usage = psutil.cpu_percent(interval=1)
    except:
        cpu_usage = "Unavailable"

    try:
        ram = psutil.virtual_memory()
        ram_total = f"{round(ram.total / (1024**3), 2)} GB"
        ram_used  = f"{round(ram.used / (1024**3), 2)} GB"
        ram_free  = f"{round(ram.available / (1024**3), 2)} GB"
    except:
        ram_total = ram_used = ram_free = "Unavailable"

    try:
        disk = psutil.disk_usage('/')
        disk_total = f"{round(disk.total / (1024**3), 2)} GB"
        disk_used  = f"{round(disk.used / (1024**3), 2)} GB"
        disk_free  = f"{round(disk.free / (1024**3), 2)} GB"
    except:
        disk_total = disk_used = disk_free = "Unavailable"

    config = (
        f"📟 Device Config\n"
        f"  Hostname     : {sock.gethostname()}\n"
        f"  IP Address   : {ip_address}\n"
        f"  OS           : {platform.system()} {platform.release()}\n"
        f"  Architecture : {platform.machine()}\n"
        f"  Processor    : {platform.processor()}\n"
        f"  CPU Cores    : {psutil.cpu_count(logical=False)} physical, "
                         f"{psutil.cpu_count(logical=True)} logical\n"
        f"  CPU Usage    : {cpu_usage}%\n"
        f"  RAM Total    : {ram_total}\n"
        f"  RAM Used     : {ram_used}\n"
        f"  RAM Free     : {ram_free}\n"
        f"  Disk Total   : {disk_total}\n"
        f"  Disk Used    : {disk_used}\n"
        f"  Disk Free    : {disk_free}\n"
        f"  Python Ver   : {platform.python_version()}\n"
    )
    return config


def receive_from_server():
    """Single thread handles ALL incoming messages from server."""
    global device_status

    while True:
        try:
            message = secure_socket.recv(4096).decode()

            if not message:
                break

            start = time.time()

            if message == "TURN_ON_LIGHT":
                device_status = "ON"
                result = "Light turned ON"
                latency = time.time() - start
                secure_socket.send(f"{result} | Latency: {latency:.5f}s".encode())
                print(f"\n📡 Server Command: {message}")
                print(f"✅ {result}")

            elif message == "TURN_OFF_LIGHT":
                device_status = "OFF"
                result = "Light turned OFF"
                latency = time.time() - start
                secure_socket.send(f"{result} | Latency: {latency:.5f}s".encode())
                print(f"\n📡 Server Command: {message}")
                print(f"✅ {result}")

            elif message == "GET_STATUS":
                result = f"Device Status: {device_status}"
                latency = time.time() - start
                secure_socket.send(f"{result} | Latency: {latency:.5f}s".encode())
                print(f"\n📡 Server Command: {message}")
                print(f"✅ {result}")

            elif message == "GET_TEMPERATURE":
                result = "Temperature: 25 C"
                latency = time.time() - start
                secure_socket.send(f"{result} | Latency: {latency:.5f}s".encode())
                print(f"\n📡 Server Command: {message}")
                print(f"✅ {result}")

            elif message == "GET_DEVICE_CONFIG":
                config = get_device_config()
                latency = time.time() - start
                payload = config + f"\n  Latency      : {latency:.5f}s"
                secure_socket.send(payload.encode())
                print(f"\n📡 Server Command: {message}")
                print(config)

            else:
                # Reply to a CLIENT: command the user typed
                print(f"\n📥 Server Reply: {message}")

            print("💻 Enter command for server: ", end="", flush=True)

        except Exception as e:
            print(f"\n⚠️  Connection to server lost: {e}")
            break


def send_to_server():
    """Only sends — never calls recv()."""
    while True:
        try:
            msg = input("💻 Enter command for server: ").strip()

            if not msg:
                continue

            secure_socket.send(("CLIENT:" + msg).encode())

            if msg == "EXIT":
                print("👋 Disconnecting...")
                break

        except KeyboardInterrupt:
            print("\n👋 Disconnecting...")
            break
        except Exception as e:
            print(f"⚠️  Error: {e}")
            break


threading.Thread(target=receive_from_server, daemon=True).start()
send_to_server()

secure_socket.close()
print("🔌 Disconnected from server.")