"""
===============================================================================
DRONE NODE - Relay Node in Emergency Mesh Network
===============================================================================
This program simulates a drone relay node that forwards emergency messages
in a multi-hop mesh network.

FEATURES:
- Receives messages from sender or other nodes
- Maintains a priority queue (HIGH > MEDIUM > LOW)
- Avoids duplicate messages using message_id tracking
- Dynamic routing: tries multiple neighbors if one fails
- Self-healing network capability

HOW TO RUN:
1. Update NODE_PORT to a unique port for this node
2. Update NEIGHBOR_NODES with IPs/ports of other nodes and base station
3. Run: python node.py
4. The node will start listening for incoming messages

NETWORK SETUP EXAMPLE:
Node 1 (5001) → Node 2 (5002) → Node 3 (5003) → Base Station (5000)

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
# CONFIGURATION - Update these for each node
# ============================================================================
NODE_PORT = 5001  # Unique port for THIS node (change for each node: 5001, 5002, 5003, etc.)
NODE_IP = "0.0.0.0"  # Listen on all interfaces

# List of neighbor nodes this node can forward messages to
# Format: (IP, PORT)
# Update this list based on your network topology
NEIGHBOR_NODES = [
    ("127.0.0.1", 5002),  # Next hop node
    ("127.0.0.1", 5000),  # Or directly to base station if in range
]

# Simulation parameters
TRANSMISSION_DELAY = 1  # Seconds to simulate transmission time
MAX_RETRIES = 3  # Maximum attempts to send to a neighbor

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================
# Priority queue for outgoing messages
message_queue = queue.PriorityQueue()

# Set to track received message IDs (prevents duplicates)
received_message_ids = set()

# Lock for thread-safe operations
lock = threading.Lock()

# Priority mapping
PRIORITY_MAP = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_priority_value(priority_str):
    """
    Converts priority string to numeric value for queue ordering
    
    Parameters:
        priority_str (str): Priority level (HIGH, MEDIUM, LOW)
    
    Returns:
        int: Numeric priority (1=highest, 3=lowest)
    """
    return PRIORITY_MAP.get(priority_str.upper(), 3)

def is_duplicate_message(message_id):
    """
    Checks if a message has already been received
    
    Parameters:
        message_id (str): Unique message identifier
    
    Returns:
        bool: True if message is duplicate, False otherwise
    """
    with lock:
        if message_id in received_message_ids:
            return True
        received_message_ids.add(message_id)
        return False

def log_message(log_type, message):
    """
    Prints formatted log messages with timestamp
    
    Parameters:
        log_type (str): Type of log (INFO, SUCCESS, ERROR, WARNING)
        message (str): Log message content
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{log_type}] {message}")

def display_message_details(message):
    """
    Displays the received message in a formatted way
    
    Parameters:
        message (dict): Message dictionary
    """
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
# MESSAGE HANDLING FUNCTIONS
# ============================================================================

def handle_incoming_message(client_socket, client_address):
    """
    Handles an incoming message from another node or sender
    
    Parameters:
        client_socket: Socket object for the connection
        client_address: Address tuple (IP, port) of sender
    """
    try:
        # Receive data
        data = client_socket.recv(4096).decode('utf-8')
        
        if not data:
            return
        
        # Parse JSON message
        message = json.loads(data)
        message_id = message.get('message_id')
        priority = message.get('priority', 'MEDIUM')
        
        log_message("INFO", f"Message received from {client_address[0]}:{client_address[1]}")
        
        # Check for duplicate
        if is_duplicate_message(message_id):
            log_message("WARNING", f"Duplicate message detected (ID: {message_id[:8]}...) - IGNORED")
            return
        
        # Display message details
        display_message_details(message)
        
        # Add to priority queue
        priority_value = get_priority_value(priority)
        message_queue.put((priority_value, time.time(), message))
        
        log_message("SUCCESS", f"Message queued with priority: {priority} (value: {priority_value})")
        log_message("INFO", f"Queue size: {message_queue.qsize()}")
        
    except json.JSONDecodeError:
        log_message("ERROR", "Invalid JSON format received")
    except Exception as e:
        log_message("ERROR", f"Error handling message: {e}")
    finally:
        client_socket.close()

def send_to_neighbor(neighbor_ip, neighbor_port, message):
    """
    Attempts to send a message to a specific neighbor node
    
    Parameters:
        neighbor_ip (str): IP address of neighbor
        neighbor_port (int): Port number of neighbor
        message (dict): Message to send
    
    Returns:
        bool: True if successful, False otherwise
    """
    for attempt in range(MAX_RETRIES):
        try:
            # Create socket and connect
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_socket.settimeout(3)  # 3 second timeout
            
            forward_socket.connect((neighbor_ip, neighbor_port))
            
            # Send message
            message_json = json.dumps(message)
            forward_socket.send(message_json.encode('utf-8'))
            
            forward_socket.close()
            
            log_message("SUCCESS", f"Forwarded to {neighbor_ip}:{neighbor_port}")
            return True
            
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            if attempt < MAX_RETRIES - 1:
                log_message("WARNING", f"Attempt {attempt + 1} failed for {neighbor_ip}:{neighbor_port}, retrying...")
                time.sleep(0.5)
            else:
                log_message("ERROR", f"Neighbor unreachable: {neighbor_ip}:{neighbor_port}")
                return False
        except Exception as e:
            log_message("ERROR", f"Unexpected error sending to {neighbor_ip}:{neighbor_port}: {e}")
            return False
    
    return False

def forward_messages():
    """
    Background thread that continuously forwards messages from the queue
    Uses priority-based forwarding with dynamic routing
    """
    log_message("INFO", "Message forwarding thread started")
    
    while True:
        try:
            # Get highest priority message (blocks until message available)
            priority_value, timestamp, message = message_queue.get(timeout=1)
            
            priority_str = message.get('priority', 'MEDIUM')
            message_id = message.get('message_id', 'Unknown')
            
            log_message("INFO", f"Processing message (Priority: {priority_str}, ID: {message_id[:8]}...)")
            
            # Simulate transmission delay (distance simulation)
            log_message("INFO", f"Simulating transmission delay ({TRANSMISSION_DELAY}s)...")
            time.sleep(TRANSMISSION_DELAY)
            
            # Try forwarding to neighbors using dynamic routing
            forwarded = False
            
            for neighbor_ip, neighbor_port in NEIGHBOR_NODES:
                log_message("INFO", f"Attempting to forward to {neighbor_ip}:{neighbor_port}...")
                
                if send_to_neighbor(neighbor_ip, neighbor_port, message):
                    forwarded = True
                    break  # Successfully forwarded, no need to try other neighbors
                else:
                    log_message("WARNING", "Trying next neighbor (dynamic routing)...")
            
            if not forwarded:
                log_message("ERROR", "FAILED: Could not forward message to any neighbor!")
                log_message("ERROR", "Message may be lost. Check network connectivity.")
            
            # Mark task as done
            message_queue.task_done()
            
        except queue.Empty:
            # No messages in queue, continue waiting
            continue
        except Exception as e:
            log_message("ERROR", f"Error in forwarding thread: {e}")
            time.sleep(1)

# ============================================================================
# SERVER FUNCTIONS
# ============================================================================

def start_server():
    """
    Starts the node server to listen for incoming messages
    Runs in the main thread
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((NODE_IP, NODE_PORT))
        server_socket.listen(5)
        
        print("\n" + "=" * 70)
        print(" " * 20 + "DRONE NODE - MESH NETWORK")
        print("=" * 70)
        log_message("INFO", f"Node listening on port {NODE_PORT}")
        log_message("INFO", f"Neighbors configured: {len(NEIGHBOR_NODES)}")
        
        for idx, (ip, port) in enumerate(NEIGHBOR_NODES, 1):
            print(f"  Neighbor {idx}: {ip}:{port}")
        
        print("=" * 70)
        log_message("SUCCESS", "Node is ready to receive and forward messages!")
        print("=" * 70 + "\n")
        
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
        log_message("ERROR", f"Port {NODE_PORT} is already in use or cannot be bound!")
        log_message("ERROR", "Please use a different port or close the existing program.")
        return
    except KeyboardInterrupt:
        log_message("INFO", "\nNode shutting down...")
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
    Main function to start the drone node
    Starts both the server and forwarding threads
    """
    # Start the message forwarding thread
    forwarding_thread = threading.Thread(target=forward_messages)
    forwarding_thread.daemon = True
    forwarding_thread.start()
    
    # Start the server (runs in main thread)
    start_server()

if __name__ == "__main__":
    main()
