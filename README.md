# SkyLink Rescue Network — Emergency Communication via Drone Nodes

**College Project - Computer Networks**

A Python-based mesh communication system where multiple laptops act as drone relay nodes in a disaster area where normal mobile networks are unavailable.

> **No editing needed!** Every script now asks for the IP address at startup. Just run, type the IP, done.

---

## 📋 Project Overview

| Script | Role | Machine |
|---|---|---|
| `base_station.py` | Final receiver — Rescue Control Center | Mac (or any) |
| `node1.py` | Drone relay node 1 | Windows Laptop 1 |
| `node2.py` | Drone relay node 2 | Windows Laptop 2 |
| `sender_client.py` | Victim device simulator | Any machine |

**Message flow:**
```
sender_client → node2 → node1 → base_station
   (port 5002)  (port 5001)   (port 5000)
```

---

## ✨ Key Features

- ✅ **Zero configuration** — IP addresses entered at runtime, no file editing
- ✅ **Cross-platform** — Works on Windows, macOS, Linux
- ✅ **Multi-hop Message Forwarding** — Messages travel through multiple nodes
- ✅ **Priority-based Transmission** — HIGH, MEDIUM, LOW priority levels
- ✅ **Dynamic Routing** — Self-healing network (if one node fails, tries next)
- ✅ **Message Deduplication** — Prevents processing the same message twice
- ✅ **Real-time Display** — Shows messages in formatted tables
- ✅ **Persistent Storage** — Saves all messages to `messages.json`

---

## 🚀 Multi-Machine Setup (3 Laptops)

> All machines must be on the **same WiFi network**.

### Step 1 — Base Station (Mac or any machine)
```bash
python base_station.py
```
- It will print this machine's IP, e.g. `192.168.1.10`
- ✏️ Tell the **Node 1 operator** this IP.

### Step 2 — Node 1 (Windows Laptop 1)
```bash
python node1.py
```
- Enter the **Base Station's IP** when prompted.
- It will print its own IP, e.g. `192.168.1.20`
- ✏️ Tell the **Node 2 operator** this IP.

### Step 3 — Node 2 (Windows Laptop 2)
```bash
python node2.py
```
- Enter **Node 1's IP** when prompted.
- It will print its own IP, e.g. `192.168.1.30`
- ✏️ Tell the **Victim (sender) operator** this IP.

### Step 4 — Sender / Victim (any machine)
```bash
python sender_client.py
```
- Enter **Node 2's IP** when prompted.
- Fill in your name, location, message, and priority — hit send!

---

## 🖥️ Single Computer Testing (Localhost)

Open 4 terminals and run each script. When asked for an IP, type `127.0.0.1`.

---

## Prerequisites

- Python 3.6 or higher (no extra libraries needed)
- All machines on the same WiFi network

---

## 🖥️ Network Setup

### Option 1: Single Computer Testing (Localhost)

Perfect for initial testing and demonstration:

```
Sender → Node1 (5001) → Node2 (5002) → Node3 (5003) → Base Station (5000)
All running on 127.0.0.1 (localhost)
```

### Option 2: Multi-Computer Network (WiFi)

For actual mesh network simulation:

```
Laptop 1 (192.168.1.10): Sender Client
Laptop 2 (192.168.1.11): Node 1 (Port 5001)
Laptop 3 (192.168.1.12): Node 2 (Port 5002)
Laptop 4 (192.168.1.13): Node 3 (Port 5003)
Laptop 5 (192.168.1.14): Base Station (Port 5000)
```

---

## 📝 Step-by-Step Setup Instructions

### Step 1: Configure Base Station

**On the Base Station laptop:**

1. Open `base_station.py`
2. Keep default settings:
   ```python
   BASE_STATION_PORT = 5000
   ```
3. Run the base station:
   ```bash
   python base_station.py
   ```
4. You should see:
   ```
   ╔════════════════════════════════════════════════════════════════════════════╗
   ║               EMERGENCY COMMUNICATION NETWORK - BASE STATION               ║
   ║                        Rescue Control Center                               ║
   ╚════════════════════════════════════════════════════════════════════════════╝
   
   [HH:MM:SS] [SUCCESS] Base station listening on port 5000
   ```

---

### Step 2: Configure Drone Nodes

**Configure each node with unique port and neighbor list:**

#### Node 1 Configuration (First Node)
```python
NODE_PORT = 5001

NEIGHBOR_NODES = [
    ("127.0.0.1", 5002),  # Node 2 (next hop)
    ("127.0.0.1", 5000),  # Base Station (if in direct range)
]
```

#### Node 2 Configuration (Middle Node)
```python
NODE_PORT = 5002

NEIGHBOR_NODES = [
    ("127.0.0.1", 5003),  # Node 3 (next hop)
    ("127.0.0.1", 5000),  # Base Station (if in direct range)
]
```

#### Node 3 Configuration (Last Node)
```python
NODE_PORT = 5003

NEIGHBOR_NODES = [
    ("127.0.0.1", 5000),  # Base Station (final destination)
]
```

**Run each node:**
```bash
python node.py
```

Expected output:
```
══════════════════════════════════════════════════════════════════════
                      DRONE NODE - MESH NETWORK
══════════════════════════════════════════════════════════════════════
[HH:MM:SS] [INFO] Node listening on port 5001
[HH:MM:SS] [INFO] Neighbors configured: 2
  Neighbor 1: 127.0.0.1:5002
  Neighbor 2: 127.0.0.1:5000
══════════════════════════════════════════════════════════════════════
[HH:MM:SS] [SUCCESS] Node is ready to receive and forward messages!
```

---

### Step 3: Configure Sender Client

**On the Sender laptop:**

1. Open `sender_client.py`
2. Update the first node's address:
   ```python
   FIRST_NODE_IP = "127.0.0.1"    # Change to Node 1's IP in WiFi setup
   FIRST_NODE_PORT = 5001          # Port of first node
   ```
3. Run the sender:
   ```bash
   python sender_client.py
   ```

---

## 🎮 Usage Examples

### Sending a High-Priority Emergency Message

1. Run `sender_client.py`
2. Enter details:
   ```
   Your Name: John Doe
   Your Location: Building A, Floor 3
   Emergency Message: Multiple people trapped, need immediate rescue
   Priority: 1 (HIGH)
   ```
3. Press 'y' to send

### What Happens:

1. **Sender Client** → Sends message to Node 1
2. **Node 1** → Receives, queues by priority, forwards to Node 2
3. **Node 2** → Receives, forwards to Node 3
4. **Node 3** → Receives, forwards to Base Station
5. **Base Station** → Displays in table and saves to `messages.json`

---

## 🔧 Configuration Guide

### For WiFi Network Setup

**Find your laptop's IP address:**

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.10)

**Mac/Linux:**
```bash
ifconfig
```
Look for "inet" under your WiFi interface

**Update configuration:**
1. Replace `127.0.0.1` with actual IP addresses
2. Ensure all laptops are on the same network
3. Disable firewalls or allow Python through firewall

### Example Multi-Computer Configuration

**Node 1 on Laptop A (192.168.1.11):**
```python
NODE_PORT = 5001
NEIGHBOR_NODES = [
    ("192.168.1.12", 5002),  # Node 2's IP
    ("192.168.1.14", 5000),  # Base Station's IP
]
```

**Sender on Laptop B:**
```python
FIRST_NODE_IP = "192.168.1.11"  # Node 1's IP
FIRST_NODE_PORT = 5001
```

---

## 🧪 Testing Scenarios

### Test 1: Basic Message Delivery
1. Start Base Station
2. Start one Node
3. Send a message from Sender
4. Verify message reaches Base Station

### Test 2: Multi-Hop Routing
1. Start Base Station
2. Start 3 Nodes in sequence
3. Send a message from Sender
4. Watch message hop through each node
5. Verify arrival at Base Station

### Test 3: Priority Handling
1. Send 3 messages with different priorities (LOW, HIGH, MEDIUM)
2. Observe that HIGH priority is forwarded first
3. Check Base Station receives in correct order

### Test 4: Dynamic Routing (Self-Healing)
1. Start Base Station and 3 Nodes
2. Send a message
3. **Stop Node 2** (simulate failure)
4. Send another message
5. Observe Node 1 tries Node 2, then routes to Base Station directly

### Test 5: Duplicate Prevention
1. Manually send the same message twice
2. First node should process once, ignore duplicate

---

## 📊 Message Structure

All messages follow this JSON format:

```json
{
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "sender_name": "John Doe",
    "location": "Building A, Floor 3",
    "message_text": "Need immediate medical assistance",
    "priority": "HIGH",
    "timestamp": "2026-02-01 14:30:45"
}
```

---

## 🎯 Priority System

| Priority | Value | Use Case |
|----------|-------|----------|
| **HIGH** | 1 | Life-threatening emergencies |
| **MEDIUM** | 2 | Urgent but not critical |
| **LOW** | 3 | Information or non-urgent requests |

Messages are forwarded in order: HIGH → MEDIUM → LOW

---

## 📁 File Structure

```
CN project/
│
├── base_station.py          # Base station receiver
├── node.py                  # Drone relay node
├── sender_client.py         # Message sender
├── messages.json            # Saved messages (auto-generated)
└── README.md               # This file
```

---

## 🐛 Troubleshooting

### Problem: "Port already in use"
**Solution:** Another program is using that port. Change the port number or close the existing program.

### Problem: "Connection refused"
**Solution:** 
- Ensure the target node/base station is running first
- Check firewall settings
- Verify IP addresses and ports are correct
- Use `127.0.0.1` for local testing

### Problem: Messages not forwarding
**Solution:**
- Check `NEIGHBOR_NODES` configuration
- Ensure neighbors are actually running
- Check network connectivity
- Review logs for error messages

### Problem: Duplicate messages appearing
**Solution:** This shouldn't happen due to deduplication. If it does:
- Ensure each message has a unique UUID
- Check if multiple nodes have same port

---

## 🔬 Advanced Customization

### Adjust Transmission Delay
In `node.py`:
```python
TRANSMISSION_DELAY = 2  # Increase to simulate longer distances
```

### Change Retry Attempts
In `node.py`:
```python
MAX_RETRIES = 5  # Increase for unreliable networks
```

### Modify Message Storage
In `base_station.py`:
```python
MESSAGES_FILE = "emergency_logs.json"  # Change filename
```

---

## 📸 Expected Output Screenshots

### Base Station Display:
```
═════════════════════════════════════════════════════════════════════════════════
                                    MESSAGE #1
═════════════════════════════════════════════════════════════════════════════════
│ Field                │ Value                                                  │
├──────────────────────┼────────────────────────────────────────────────────────┤
│ Message ID           │ 550e8400-e29b-41d4-a716-446655440000                   │
│ Sender Name          │ John Doe                                               │
│ Location             │ Building A, Floor 3                                    │
│ Priority             │ HIGH ⚠️                                                 │
│ Timestamp            │ 2026-02-01 14:30:45                                    │
├──────────────────────┴────────────────────────────────────────────────────────┤
│ MESSAGE CONTENT                                                               │
├───────────────────────────────────────────────────────────────────────────────┤
│ Need immediate medical assistance                                            │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Node Display:
```
══════════════════════════════════════════════════════════════════════
NEW MESSAGE RECEIVED:
══════════════════════════════════════════════════════════════════════
Message ID  : 550e8400-e29b-41d4-a716-446655440000
Sender      : John Doe
Location    : Building A, Floor 3
Message     : Need immediate medical assistance
Priority    : HIGH
Timestamp   : 2026-02-01 14:30:45
══════════════════════════════════════════════════════════════════════

[14:30:45] [SUCCESS] Message queued with priority: HIGH (value: 1)
[14:30:45] [INFO] Queue size: 1
[14:30:46] [INFO] Processing message (Priority: HIGH, ID: 550e8400...)
[14:30:46] [INFO] Simulating transmission delay (1s)...
[14:30:47] [INFO] Attempting to forward to 127.0.0.1:5002...
[14:30:47] [SUCCESS] Forwarded to 127.0.0.1:5002
```

---

## 🎓 Learning Objectives

This project demonstrates:

1. **Socket Programming** - TCP client-server communication
2. **Multi-threading** - Concurrent message handling
3. **Priority Queues** - Data structure for prioritization
4. **Network Protocols** - JSON message format
5. **Routing Algorithms** - Dynamic multi-hop forwarding
6. **Fault Tolerance** - Self-healing network design
7. **File I/O** - Persistent message storage

---

## 📚 Project Report Tips

Include in your report:

1. **System Architecture Diagram** - Show node topology
2. **Message Flow Diagram** - Illustrate multi-hop routing
3. **Algorithm Explanation** - Priority queue and routing logic
4. **Test Results** - Screenshots of different scenarios
5. **Performance Analysis** - Message delivery time, success rate
6. **Challenges Faced** - Network issues, debugging stories
7. **Future Improvements** - GPS integration, encryption, etc.

---

## 🔮 Future Enhancements

Possible improvements for advanced versions:

- 🔐 **Encryption** - Secure message transmission
- 📍 **GPS Integration** - Real location tracking
- 🌐 **Web Interface** - Browser-based control panel
- 📊 **Real-time Dashboard** - Visualize network topology
- 🔔 **Audio Alerts** - Sound notifications for high-priority messages
- 📱 **Mobile App** - Android/iOS sender client
- 🤖 **AI-based Routing** - Machine learning for optimal paths

---

## 👥 Team Roles Suggestion

If working in a team:

- **Member 1:** Base Station + Documentation
- **Member 2:** Drone Node + Routing Logic
- **Member 3:** Sender Client + Testing
- **Member 4:** Network Setup + Presentation

---

## 📞 Support

For questions or issues:

1. Check the Troubleshooting section
2. Review code comments - they're very detailed
3. Test with localhost first before WiFi setup
4. Consult your instructor or teaching assistant

---

## 📜 License

This is an educational project for college coursework. Feel free to use and modify for learning purposes.

---

## ✅ Submission Checklist

Before submitting your project:

- [ ] All three Python files are present and working
- [ ] Code has clear comments
- [ ] Successfully tested on localhost
- [ ] Successfully tested on WiFi network (if required)
- [ ] Screenshots of working system
- [ ] `messages.json` with sample messages
- [ ] README is updated with your team info
- [ ] Project report is complete
- [ ] Presentation slides are ready

---

## 🎉 Good Luck!

This project demonstrates a real-world application of computer networks in disaster management. The concepts you learn here are used in actual emergency communication systems, drone swarms, and IoT networks.

**Remember:** Start with localhost testing, then move to WiFi. Test each component individually before combining them.

---

**Project Title:** Simulation of an Emergency Communication Network Using Drone Nodes  
**Course:** Computer Networks (CN)  
**Semester:** 4th Semester  
**Year:** 2026
