"""
===============================================================================
SENDER CLIENT - Victim Device Simulator  (runs on Mac / any machine)
===============================================================================
Simulates a victim sending an emergency message into the mesh network.

HOW TO RUN:
1. Make sure node2.py is running on its machine.
2. Run: python sender_client.py
3. When prompted, enter Node 2's IP address.
4. Fill in your details and send the message.

CHAIN:  Victim (this script) → Node 2 → Node 1 → Base Station

AUTHOR: College Project - Emergency Communication Network
===============================================================================
"""

import socket
import json
import uuid
from datetime import datetime

# ============================================================================
# CONFIGURATION  (set at runtime - no editing needed)
# ============================================================================
FIRST_NODE_IP   = None  # Will be asked at startup
FIRST_NODE_PORT = 5002  # Node 2 always listens on 5002

# ============================================================================
# MESSAGE CREATION
# ============================================================================

def create_message(sender_name, location, message_text, priority):
    """
    Creates a properly formatted emergency message in JSON format
    
    Parameters:
        sender_name (str): Name of the person sending the message
        location (str): Location of the sender
        message_text (str): The actual emergency message
        priority (str): Priority level - HIGH, MEDIUM, or LOW
    
    Returns:
        dict: A complete message dictionary ready to be sent
    """
    message = {
        "message_id": str(uuid.uuid4()),  # Unique identifier for this message
        "sender_name": sender_name,
        "location": location,
        "message_text": message_text,
        "priority": priority.upper(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return message

# ============================================================================
# SEND
# ============================================================================

def send_message(message):
    """
    Sends the message to the first drone node in the mesh network
    
    Parameters:
        message (dict): The message dictionary to send
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)

        print(f"\n[INFO] Connecting to Node 2 at {FIRST_NODE_IP}:{FIRST_NODE_PORT}...")
        client_socket.connect((FIRST_NODE_IP, FIRST_NODE_PORT))

        client_socket.send(json.dumps(message).encode('utf-8'))

        print(f"[SUCCESS] Message sent successfully!")
        print(f"[INFO] Message ID: {message['message_id']}")
        client_socket.close()
        return True

    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to {FIRST_NODE_IP}:{FIRST_NODE_PORT}")
        print("[ERROR] Make sure node2.py is running on that machine!")
        return False
    except socket.timeout:
        print("[ERROR] Connection timed out. Node may be unreachable.")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
        return False

# ============================================================================
# UI HELPERS
# ============================================================================

def display_banner():
    """Displays the welcome banner"""
    print("=" * 70)
    print(" " * 15 + "EMERGENCY COMMUNICATION SYSTEM")
    print(" " * 20 + "Victim Device Simulator")
    print("=" * 70)

def get_priority_input():
    """
    Gets priority input from user with validation
    
    Returns:
        str: Valid priority level (HIGH, MEDIUM, or LOW)
    """
    print("\nSelect Priority Level:")
    print("  1. HIGH   - Life-threatening emergency")
    print("  2. MEDIUM - Urgent but not critical")
    print("  3. LOW    - Information or non-urgent")
    while True:
        choice = input("\nEnter choice (1/2/3): ").strip()
        if choice == "1":
            return "HIGH"
        elif choice == "2":
            return "MEDIUM"
        elif choice == "3":
            return "LOW"
        else:
            print("[ERROR] Invalid choice. Please enter 1, 2, or 3.")

# ============================================================================
# MAIN
# ============================================================================

def main():
    global FIRST_NODE_IP

    display_banner()

    # Ask for Node 2 IP once at startup
    print()
    while True:
        ip = input("Enter NODE 2 machine's IP address: ").strip()
        if ip:
            FIRST_NODE_IP = ip
            break
        print("[ERROR] IP cannot be empty. Try again.")

    print(f"\n[OK] Will send messages to Node 2 at {FIRST_NODE_IP}:{FIRST_NODE_PORT}")
    print("\nThis simulator allows you to send emergency messages")
    print("through the drone mesh network to the base station.\n")

    while True:
        try:
            print("\n" + "-" * 70)
            print("Enter Emergency Message Details:")
            print("-" * 70)

            sender_name = input("\nYour Name: ").strip()
            if not sender_name:
                print("[ERROR] Name cannot be empty!")
                continue

            location = input("Your Location: ").strip()
            if not location:
                print("[ERROR] Location cannot be empty!")
                continue

            message_text = input("Emergency Message: ").strip()
            if not message_text:
                print("[ERROR] Message cannot be empty!")
                continue

            priority = get_priority_input()

            message = create_message(sender_name, location, message_text, priority)

            print("\n" + "=" * 70)
            print("MESSAGE PREVIEW:")
            print("=" * 70)
            print(f"Sender Name : {message['sender_name']}")
            print(f"Location    : {message['location']}")
            print(f"Message     : {message['message_text']}")
            print(f"Priority    : {message['priority']}")
            print(f"Timestamp   : {message['timestamp']}")
            print("=" * 70)

            confirm = input("\nSend this message? (y/n): ").strip().lower()

            if confirm == 'y':
                success = send_message(message)
                if success:
                    print("\n[SUCCESS] Your emergency message has been transmitted!")
                    print("[INFO] It will be relayed through drone nodes to the base station.\n")
            else:
                print("\n[CANCELLED] Message not sent.")

            another = input("\nSend another message? (y/n): ").strip().lower()
            if another != 'y':
                print("\n[INFO] Exiting sender client. Stay safe!")
                break

        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            continue

if __name__ == "__main__":
    main()
