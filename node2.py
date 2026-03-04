"""
===============================================================================
DRONE NODE 2 - Relay Node  (runs on Windows Laptop 2)
===============================================================================
This node receives messages from the Victim (sender_client) and forwards
them to Node 1, which then sends them to the Base Station.

HOW TO RUN:
1. Make sure node1.py is already running on its machine.
2. Run on this machine:  python node2.py
3. When prompted, enter Node 1's IP address.
4. Share THIS machine's IP with the person running sender_client.py.

CHAIN:  Victim (sender_client) → Node 2 → Node 1 → Base Station

AUTHOR: College Project - Emergency Communication Network
===============================================================================
"""

import socket
import json
import threading
import time
import queue
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
NODE_PORT = 5002        # Port this node listens on
NODE_IP   = "0.0.0.0"  # Listen on all interfaces

TRANSMISSION_DELAY = 1  # Seconds to simulate transmission delay
MAX_RETRIES        = 3  # Max send attempts per neighbor

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================
message_queue        = queue.PriorityQueue()
received_message_ids = set()
lock                 = threading.Lock()

PRIORITY_MAP = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}

# Will be filled at startup
NEIGHBOR_NODES = []  # [(ip, port), ...]

# ============================================================================
# HELPER: detect own LAN IP
# ============================================================================
def get_my_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_priority_value(priority_str):
    return PRIORITY_MAP.get(priority_str.upper(), 3)

def is_duplicate_message(message_id):
    with lock:
        if message_id in received_message_ids:
            return True
        received_message_ids.add(message_id)
        return False

def log_message(log_type, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{log_type}] {message}")

def display_message_details(message):
    print("\n" + "=" * 70)
    print("NEW MESSAGE RECEIVED:")
    print("=" * 70)
    print(f"Message ID  : {message.get('message_id', 'N/A')}")
    print(f"Sender      : {message.get('sender_name', 'Unknown')}")
    print(f"Location    : {message.get('location', 'Unknown')}")
    print(f"Message     : {message.get('message_text', 'N/A')}")
    print(f"Priority    : {message.get('priority', 'MEDIUM')}")
    print(f"Timestamp   : {message.get('timestamp', 'N/A')}")
    print("=" * 70 + "\n")

# ============================================================================
# MESSAGE HANDLING
# ============================================================================

def handle_incoming_message(client_socket, client_address):
    try:
        data = client_socket.recv(4096).decode('utf-8')
        if not data:
            return
        message    = json.loads(data)
        message_id = message.get('message_id')
        priority   = message.get('priority', 'MEDIUM')

        log_message("INFO", f"Message received from {client_address[0]}:{client_address[1]}")

        if is_duplicate_message(message_id):
            log_message("WARNING", f"Duplicate message (ID: {message_id[:8]}...) - IGNORED")
            return

        display_message_details(message)

        priority_value = get_priority_value(priority)
        message_queue.put((priority_value, time.time(), message))

        log_message("SUCCESS", f"Message queued with priority: {priority}")
        log_message("INFO",    f"Queue size: {message_queue.qsize()}")

    except json.JSONDecodeError:
        log_message("ERROR", "Invalid JSON received")
    except Exception as e:
        log_message("ERROR", f"Error handling message: {e}")
    finally:
        client_socket.close()

def send_to_neighbor(neighbor_ip, neighbor_port, message):
    for attempt in range(MAX_RETRIES):
        try:
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_socket.settimeout(3)
            forward_socket.connect((neighbor_ip, neighbor_port))
            forward_socket.send(json.dumps(message).encode('utf-8'))
            forward_socket.close()
            log_message("SUCCESS", f"Forwarded to {neighbor_ip}:{neighbor_port}")
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            if attempt < MAX_RETRIES - 1:
                log_message("WARNING", f"Attempt {attempt + 1} failed for {neighbor_ip}:{neighbor_port}, retrying...")
                time.sleep(0.5)
            else:
                log_message("ERROR", f"Neighbor unreachable: {neighbor_ip}:{neighbor_port}")
                return False
        except Exception as e:
            log_message("ERROR", f"Unexpected error: {e}")
            return False
    return False

def forward_messages():
    log_message("INFO", "Message forwarding thread started")
    while True:
        try:
            priority_value, timestamp, message = message_queue.get(timeout=1)
            priority_str = message.get('priority', 'MEDIUM')
            message_id   = message.get('message_id', 'Unknown')

            log_message("INFO", f"Processing message (Priority: {priority_str}, ID: {message_id[:8]}...)")
            log_message("INFO", f"Simulating transmission delay ({TRANSMISSION_DELAY}s)...")
            time.sleep(TRANSMISSION_DELAY)

            forwarded = False
            for neighbor_ip, neighbor_port in NEIGHBOR_NODES:
                log_message("INFO", f"Forwarding to {neighbor_ip}:{neighbor_port}...")
                if send_to_neighbor(neighbor_ip, neighbor_port, message):
                    forwarded = True
                    break
                else:
                    log_message("WARNING", "Trying next neighbor...")

            if not forwarded:
                log_message("ERROR", "FAILED: Could not forward message to any neighbor!")

            message_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            log_message("ERROR", f"Error in forwarding thread: {e}")
            time.sleep(1)

# ============================================================================
# SERVER
# ============================================================================

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((NODE_IP, NODE_PORT))
        server_socket.listen(5)

        my_ip = get_my_ip()

        print("\n" + "=" * 70)
        print(" " * 20 + "DRONE NODE 2 - MESH NETWORK")
        print("=" * 70)
        print(f"  ✅  NODE 2 IS RUNNING")
        print(f"  📡  This machine's IP  : {my_ip}")
        print(f"  🔌  Listening on port  : {NODE_PORT}")
        print(f"  ➡️   Forwarding to      : {NEIGHBOR_NODES}")
        print()
        print("  👉  Share this IP with the person running sender_client.py")
        print("       They will enter it when prompted.")
        print("=" * 70)
        log_message("SUCCESS", "Node 2 is ready to receive and forward messages!")
        print("=" * 70 + "\n")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_incoming_message,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()

    except OSError:
        log_message("ERROR", f"Port {NODE_PORT} is already in use! Close any other instance first.")
        return
    except KeyboardInterrupt:
        log_message("INFO", "\nNode 2 shutting down...")
    except Exception as e:
        log_message("ERROR", f"Server error: {e}")
    finally:
        server_socket.close()
        log_message("INFO", "Server socket closed")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print(" " * 20 + "DRONE NODE 2 - SETUP")
    print("=" * 70)
    print("This node receives messages from the victim and forwards to Node 1.")
    print()

    # Ask for Node 1 IP
    while True:
        n1_ip = input("Enter NODE 1 machine's IP address: ").strip()
        if n1_ip:
            break
        print("[ERROR] IP cannot be empty. Try again.")

    NEIGHBOR_NODES.append((n1_ip, 5001))
    print(f"[OK] Will forward to Node 1 at {n1_ip}:5001\n")

    # Start forwarding thread
    forwarding_thread = threading.Thread(target=forward_messages)
    forwarding_thread.daemon = True
    forwarding_thread.start()

    # Start server
    start_server()

if __name__ == "__main__":
    main()
