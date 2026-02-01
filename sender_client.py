"""
===============================================================================
SENDER CLIENT - Emergency Message Sender (Victim Device Simulator)
===============================================================================
This program simulates a victim's device sending emergency messages
to the mesh network.

HOW TO RUN:
1. Make sure at least one node.py is running
2. Update FIRST_NODE_IP and FIRST_NODE_PORT to match your first drone node
3. Run: python sender_client.py
4. Enter your details and send emergency messages

AUTHOR: College Project - Emergency Communication Network
===============================================================================
"""

import socket
import json
import uuid
from datetime import datetime

# ============================================================================
# CONFIGURATION - Update these values based on your network setup
# ============================================================================
FIRST_NODE_IP = "127.0.0.1"  # IP of first drone node (use actual IP in WiFi setup)
FIRST_NODE_PORT = 5001       # Port of first drone node

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

def send_message(message):
    """
    Sends the message to the first drone node in the mesh network
    
    Parameters:
        message (dict): The message dictionary to send
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)  # 5 second timeout
        
        # Connect to the first node
        print(f"\n[INFO] Connecting to first node at {FIRST_NODE_IP}:{FIRST_NODE_PORT}...")
        client_socket.connect((FIRST_NODE_IP, FIRST_NODE_PORT))
        
        # Convert message to JSON and send
        message_json = json.dumps(message)
        client_socket.send(message_json.encode('utf-8'))
        
        print(f"[SUCCESS] Message sent successfully!")
        print(f"[INFO] Message ID: {message['message_id']}")
        
        # Close connection
        client_socket.close()
        return True
        
    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to node at {FIRST_NODE_IP}:{FIRST_NODE_PORT}")
        print("[ERROR] Make sure the first drone node is running!")
        return False
    except socket.timeout:
        print("[ERROR] Connection timeout. Node may be unreachable.")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
        return False

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

def main():
    """Main function to run the sender client"""
    display_banner()
    
    print(f"\n[CONFIG] First Node: {FIRST_NODE_IP}:{FIRST_NODE_PORT}")
    print("\nThis simulator allows you to send emergency messages")
    print("through the drone mesh network to the base station.\n")
    
    while True:
        try:
            print("\n" + "-" * 70)
            print("Enter Emergency Message Details:")
            print("-" * 70)
            
            # Get user input
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
            
            # Create and display the message
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
            
            # Confirm before sending
            confirm = input("\nSend this message? (y/n): ").strip().lower()
            
            if confirm == 'y':
                # Send the message
                success = send_message(message)
                
                if success:
                    print("\n[SUCCESS] Your emergency message has been transmitted!")
                    print("[INFO] The message will be relayed through drone nodes")
                    print("[INFO] to reach the base station.\n")
            else:
                print("\n[CANCELLED] Message not sent.")
            
            # Ask if user wants to send another message
            another = input("\nSend another message? (y/n): ").strip().lower()
            if another != 'y':
                print("\n[INFO] Exiting sender client. Stay safe!")
                break
                
        except KeyboardInterrupt:
            print("\n\n[INFO] Program interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] An unexpected error occurred: {e}")
            continue

if __name__ == "__main__":
    main()
