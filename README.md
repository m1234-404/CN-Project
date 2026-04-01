# Remote Device Control and Monitoring System

## 📌 Project Description
This project implements a secure multi-client Remote Device Control and Monitoring System using TCP socket programming and SSL encryption. The system allows a central server to control and monitor multiple client devices in real-time.

---

## Objectives
- Implement TCP-based client-server communication
- Support multiple clients simultaneously
- Ensure secure communication using SSL/TLS
- Enable remote device control and monitoring
- Measure latency of command execution

---

## System Architecture

- Server acts as a **central controller**
- Clients act as **remote devices**
- Communication is **bidirectional**
- All communication is secured using **SSL**

---

## Features

✔ Multi-client support  
✔ SSL/TLS secure communication  
✔ Authentication (username/password)  
✔ Server-controlled device commands  
✔ Client-to-server command communication  
✔ Device status monitoring  
✔ Latency measurement  
✔ Reliable acknowledgment system  

---

## Commands Supported
TURN_ON_LIGHT
TURN_OFF_LIGHT
GET_STATUS
GET_DEVICE_CONFIG
GET_TEMPERATURE
EXIT


---

## Communication Flow

### Server → Client
- Sends control commands
- Client executes and returns response with latency

### Client → Server
- Sends commands or status requests
- Server processes and responds

---

## Security Implementation

- SSL/TLS used for encryption
- Self-signed certificate generated using OpenSSL
- Secure socket wrapping on both client and server

---

## Latency Measurement

Latency is calculated as:
Latency = Response Time - Request Time

Each response includes execution time in seconds.

---

## How to Run

### Step 1: Generate SSL Certificate
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes


### Step 2: Run Server
python server.py


### Step 3: Run Clients (multiple terminals)
python client.py


## Example Output
Server Command: TURN_ON_LIGHT
Client Response: Light turned ON | Latency: 0.00012 sec

---

## Performance

- Supports multiple clients using threading
- Low latency communication
- Reliable TCP transmission

---

## Conclusion

This project demonstrates a secure and efficient remote device monitoring system using TCP sockets, SSL encryption, and multi-client architecture with real-time command execution and performance analysis.

---

## Technologies Used

- Python
- Socket Programming
- SSL/TLS
- Multi-threading


