"""
===============================================================================
BASE STATION - Rescue Control Center
===============================================================================
Receives all relayed emergency messages from drone nodes.

HOW TO RUN:
1. Run this FIRST on the Base Station machine (any OS).
2. It will print this machine's IP — share that IP with the Node 1 operator.
3. python base_station.py

AUTHOR: College Project - Emergency Communication Network
===============================================================================
"""

import socket
import json
import threading
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_STATION_PORT = 5000        # Port this station listens on
BASE_STATION_IP   = "0.0.0.0"  # Listen on all network interfaces
MESSAGES_FILE     = "messages.json"

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================
received_messages = []
message_count     = 0
lock              = threading.Lock()

# ============================================================================
# HELPER: detect own LAN IP
# ============================================================================
def get_my_ip():
    """Returns this machine's LAN IP address."""
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

def log_message(log_type, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{log_type}] {message}")

def load_existing_messages():
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
                log_message("INFO", f"Loaded {len(messages)} existing messages from {MESSAGES_FILE}")
                return messages
        except Exception as e:
            log_message("WARNING", f"Could not load existing messages: {e}")
    return []

def save_message_to_file(message):
    with lock:
        try:
            received_messages.append(message)
            with open(MESSAGES_FILE, 'w') as f:
                json.dump(received_messages, f, indent=4)
            log_message("SUCCESS", f"Message saved to {MESSAGES_FILE}")
        except Exception as e:
            log_message("ERROR", f"Failed to save message: {e}")

def display_message_table(message, msg_number):
    priority = message.get('priority', 'MEDIUM')
    if priority == 'HIGH':
        priority_display = f"{priority} ⚠️"
    elif priority == 'MEDIUM':
        priority_display = f"{priority} ⚡"
    else:
        priority_display = f"{priority} ℹ️"

    print("\n" + "═" * 80)
    print(f"{'MESSAGE #' + str(msg_number):^80}")
    print("═" * 80)
    print(f"│ {'Field':<20} │ {'Value':<54} │")
    print("├" + "─" * 21 + "┼" + "─" * 55 + "┤")
    print(f"│ {'Message ID':<20} │ {message.get('message_id', 'N/A'):<54} │")
    print(f"│ {'Sender Name':<20} │ {message.get('sender_name', 'Unknown'):<54} │")
    print(f"│ {'Location':<20} │ {message.get('location', 'Unknown'):<54} │")
    print(f"│ {'Priority':<20} │ {priority_display:<54} │")
    print(f"│ {'Timestamp':<20} │ {message.get('timestamp', 'N/A'):<54} │")
    print("├" + "─" * 21 + "┴" + "─" * 55 + "┤")
    print(f"│ {'MESSAGE CONTENT':<78} │")
    print("├" + "─" * 79 + "┤")

    message_text = message.get('message_text', 'N/A')
    max_width = 76
    words = message_text.split()
    lines, current_line = [], ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    for line in lines:
        print(f"│ {line:<77} │")
    print("└" + "─" * 79 + "┘")

def display_statistics():
    if not received_messages:
        return
    high_count   = sum(1 for m in received_messages if m.get('priority') == 'HIGH')
    medium_count = sum(1 for m in received_messages if m.get('priority') == 'MEDIUM')
    low_count    = sum(1 for m in received_messages if m.get('priority') == 'LOW')
    print("\n" + "─" * 80)
    print("STATISTICS:")
    print("─" * 80)
    print(f"  Total Messages Received: {len(received_messages)}")
    print(f"  HIGH Priority:           {high_count}")
    print(f"  MEDIUM Priority:         {medium_count}")
    print(f"  LOW Priority:            {low_count}")
    print("─" * 80 + "\n")

# ============================================================================
# MESSAGE HANDLING
# ============================================================================

def handle_incoming_message(client_socket, client_address):
    global message_count
    try:
        data = client_socket.recv(4096).decode('utf-8')
        if not data:
            return
        message = json.loads(data)
        log_message("INFO", f"Message received from drone node at {client_address[0]}:{client_address[1]}")
        message_count += 1
        display_message_table(message, message_count)
        save_message_to_file(message)
        display_statistics()
        log_message("SUCCESS", f"Message #{message_count} processed successfully")
    except json.JSONDecodeError:
        log_message("ERROR", "Invalid JSON format received")
    except Exception as e:
        log_message("ERROR", f"Error handling message: {e}")
    finally:
        client_socket.close()

# ============================================================================
# SERVER
# ============================================================================

def start_base_station():
    global received_messages
    received_messages = load_existing_messages()

    my_ip = get_my_ip()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((BASE_STATION_IP, BASE_STATION_PORT))
        server_socket.listen(5)

        print("\n" + "╔" + "═" * 78 + "╗")
        print("║" + " " * 15 + "EMERGENCY COMMUNICATION NETWORK - BASE STATION" + " " * 16 + "║")
        print("║" + " " * 20 + "Rescue Control Center" + " " * 36 + "║")
        print("╚" + "═" * 78 + "╝\n")

        print("  ✅  BASE STATION IS RUNNING")
        print(f"  📡  This machine's IP : {my_ip}")
        print(f"  🔌  Listening on port : {BASE_STATION_PORT}")
        print()
        print("  👉  Share this IP with the person running node1.py")
        print("       They will enter it when prompted.")
        print()
        print("─" * 80)
        print("Waiting for emergency messages from drone network...")
        print("─" * 80 + "\n")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_incoming_message,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()

    except OSError:
        log_message("ERROR", f"Port {BASE_STATION_PORT} is already in use! Close any other instance first.")
        return
    except KeyboardInterrupt:
        print("\n")
        log_message("INFO", "Base station shutting down...")
        display_statistics()
        log_message("INFO", f"Total messages received: {message_count}")
        log_message("INFO", f"All messages saved to: {MESSAGES_FILE}")
    except Exception as e:
        log_message("ERROR", f"Server error: {e}")
    finally:
        server_socket.close()
        log_message("INFO", "Server socket closed")

# ============================================================================
# MAIN
# ============================================================================

def main():
    start_base_station()

if __name__ == "__main__":
    main()
