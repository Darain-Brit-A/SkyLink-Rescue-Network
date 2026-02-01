"""
===============================================================================
BASE STATION - Rescue Control Center
===============================================================================
This program acts as the final receiver in the emergency mesh network.
It collects all messages relayed through drone nodes and displays them
for rescue coordinators.

FEATURES:
- Receives messages from the last hop drone node
- Displays messages in a formatted table
- Saves all messages to messages.json file
- Does NOT forward messages further (final destination)

HOW TO RUN:
1. Run this program FIRST before starting nodes
2. Run: python base_station.py
3. The base station will listen for incoming messages
4. All received messages are displayed and saved to messages.json

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
BASE_STATION_PORT = 5000  # Port for base station
BASE_STATION_IP = "0.0.0.0"  # Listen on all interfaces
MESSAGES_FILE = "messages.json"  # File to store received messages

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================
received_messages = []  # List to store all received messages
message_count = 0  # Counter for received messages
lock = threading.Lock()  # Thread lock for safe file operations

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log_message(log_type, message):
    """
    Prints formatted log messages with timestamp
    
    Parameters:
        log_type (str): Type of log (INFO, SUCCESS, ERROR, WARNING)
        message (str): Log message content
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{log_type}] {message}")

def load_existing_messages():
    """
    Loads existing messages from the JSON file if it exists
    
    Returns:
        list: List of previously saved messages
    """
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
                log_message("INFO", f"Loaded {len(messages)} existing messages from {MESSAGES_FILE}")
                return messages
        except Exception as e:
            log_message("WARNING", f"Could not load existing messages: {e}")
            return []
    return []

def save_message_to_file(message):
    """
    Saves a message to the messages.json file
    Thread-safe operation using lock
    
    Parameters:
        message (dict): Message to save
    """
    with lock:
        try:
            # Add to in-memory list
            received_messages.append(message)
            
            # Write to file (overwrites with complete list)
            with open(MESSAGES_FILE, 'w') as f:
                json.dump(received_messages, f, indent=4)
            
            log_message("SUCCESS", f"Message saved to {MESSAGES_FILE}")
            
        except Exception as e:
            log_message("ERROR", f"Failed to save message: {e}")

def display_message_table(message, msg_number):
    """
    Displays a message in a formatted table view
    
    Parameters:
        message (dict): Message dictionary
        msg_number (int): Sequential message number
    """
    # Priority color coding for display
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
    
    # Word wrap for long messages
    message_text = message.get('message_text', 'N/A')
    max_width = 76
    words = message_text.split()
    lines = []
    current_line = ""
    
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
    """
    Displays statistics about received messages
    """
    if not received_messages:
        return
    
    # Count by priority
    high_count = sum(1 for m in received_messages if m.get('priority') == 'HIGH')
    medium_count = sum(1 for m in received_messages if m.get('priority') == 'MEDIUM')
    low_count = sum(1 for m in received_messages if m.get('priority') == 'LOW')
    
    print("\n" + "─" * 80)
    print("STATISTICS:")
    print("─" * 80)
    print(f"  Total Messages Received: {len(received_messages)}")
    print(f"  HIGH Priority:           {high_count}")
    print(f"  MEDIUM Priority:         {medium_count}")
    print(f"  LOW Priority:            {low_count}")
    print("─" * 80 + "\n")

# ============================================================================
# MESSAGE HANDLING FUNCTIONS
# ============================================================================

def handle_incoming_message(client_socket, client_address):
    """
    Handles an incoming message from a drone node
    
    Parameters:
        client_socket: Socket object for the connection
        client_address: Address tuple (IP, port) of sender
    """
    global message_count
    
    try:
        # Receive data
        data = client_socket.recv(4096).decode('utf-8')
        
        if not data:
            return
        
        # Parse JSON message
        message = json.loads(data)
        
        log_message("INFO", f"Message received from drone node at {client_address[0]}:{client_address[1]}")
        
        # Increment message counter
        message_count += 1
        
        # Display the message
        display_message_table(message, message_count)
        
        # Save to file
        save_message_to_file(message)
        
        # Display statistics
        display_statistics()
        
        log_message("SUCCESS", f"Message #{message_count} processed successfully")
        
    except json.JSONDecodeError:
        log_message("ERROR", "Invalid JSON format received")
    except Exception as e:
        log_message("ERROR", f"Error handling message: {e}")
    finally:
        client_socket.close()

# ============================================================================
# SERVER FUNCTIONS
# ============================================================================

def start_base_station():
    """
    Starts the base station server to listen for incoming messages
    """
    global received_messages
    
    # Load existing messages
    received_messages = load_existing_messages()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((BASE_STATION_IP, BASE_STATION_PORT))
        server_socket.listen(5)
        
        print("\n" + "╔" + "═" * 78 + "╗")
        print("║" + " " * 15 + "EMERGENCY COMMUNICATION NETWORK - BASE STATION" + " " * 16 + "║")
        print("║" + " " * 20 + "Rescue Control Center" + " " * 36 + "║")
        print("╚" + "═" * 78 + "╝\n")
        
        log_message("SUCCESS", f"Base station listening on port {BASE_STATION_PORT}")
        log_message("INFO", f"Messages will be saved to: {MESSAGES_FILE}")
        
        print("\n" + "─" * 80)
        print("Waiting for emergency messages from drone network...")
        print("─" * 80 + "\n")
        
        while True:
            # Accept incoming connections
            client_socket, client_address = server_socket.accept()
            
            # Handle each connection in a new thread
            client_thread = threading.Thread(
                target=handle_incoming_message,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except OSError as e:
        log_message("ERROR", f"Port {BASE_STATION_PORT} is already in use!")
        log_message("ERROR", "Please close the existing program or use a different port.")
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
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function to start the base station
    """
    start_base_station()

if __name__ == "__main__":
    main()
