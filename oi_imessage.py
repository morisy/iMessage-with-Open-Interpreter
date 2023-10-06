import os
import sqlite3
import time
import interpreter
import subprocess
import signal
import sys

database_path = f'/Users/{os.environ.get("LOGNAME") or os.environ.get("USER")}/Library/Messages/chat.db'
seen_messages = []
verbose_mode = False
send_message_in_paragraphs = True

def verbose_print(message):
    if verbose_mode:
        print(message)

def get_last_five_contacts():
    verbose_print("Getting the last five contacts...")
    conn = sqlite3.connect(database_path)
    curs = conn.cursor()
    
    # Query to get the last 20 recent contacts
    curs.execute("""
        SELECT DISTINCT id 
        FROM handle 
        JOIN message ON handle.ROWID = message.handle_id 
        ORDER BY message.date DESC 
        LIMIT 20;
    """)
    
    contacts = [item[0] for item in curs.fetchall()]
    conn.close()

    # Filtering contacts using get_latest_imessage_from_contact
    valid_contacts = []
    for contact in contacts:
        verbose_print(f"Checking if contact {contact} has a valid iMessage...")
        if get_latest_imessage_from_contact(contact) is not None:
            valid_contacts.append(contact)
        if len(valid_contacts) == 5:
            break

    return valid_contacts

def get_latest_imessage_from_contact(contact):
    verbose_print(f"Getting the latest iMessage from contact {contact}...")
    conn = sqlite3.connect(database_path)
    curs = conn.cursor()
    curs.execute("SELECT ROWID FROM handle WHERE id=?", (contact,))
    handle_id = curs.fetchone()
    if not handle_id:
        return None

    curs.execute("SELECT text FROM message WHERE handle_id=? ORDER BY date DESC LIMIT 1;", (handle_id[0],))
    message_data = curs.fetchone()
    last_rowid = None

    # If message_data is None or is an empty string, try the next older message
    while not message_data or not message_data[0].strip():
        curs.execute("SELECT text, ROWID FROM message WHERE handle_id=? AND (ROWID<? OR ? IS NULL) AND text IS NOT NULL AND text != '' ORDER BY date DESC LIMIT 1;", (handle_id[0], last_rowid, last_rowid))
        message_data = curs.fetchone()

        # If there's no further data or if we're repeating the same rowid, break out of the loop
        if not message_data or message_data[1] == last_rowid:
            break
        
        last_rowid = message_data[1]

    conn.close()
    return message_data[0] if message_data else None


def send_message(contact, message):
    global seen_messages
    verbose_print(f"Sending message to {contact}: {message}")

    chunk_size = 1000
    message_chunks = [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]

    for chunk in message_chunks:

        # Escape double quotes and backslashes for AppleScript
        chunk_escaped = chunk.replace("\\", "\\\\").replace("\"", "\\\"")

        seen_messages.append(chunk_escaped)
        
        applescript = f'''
        tell application "Messages"
            set targetBuddy to "{contact}"
            send "{chunk_escaped}" to buddy targetBuddy of (service 1 whose service type is iMessage)
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', applescript], check=True)
        except subprocess.CalledProcessError as e:
            print(f"AppleScript execution failed: {e}")

def process_message(contact, message):
    accumulated_response = ""
    for chunk in interpreter.chat(message, stream=True):
        if 'message' in chunk:
            accumulated_response += chunk['message']
        if send_message_in_paragraphs:
            if '\n' in accumulated_response.strip():
                split_response = accumulated_response.split('\n')
                before_newline = split_response[0]
                after_newline = split_response[-1]
                send_message(contact, before_newline)
                accumulated_response = after_newline.strip()
        if 'end_of_execution' in chunk or 'executing' in chunk or 'code' in chunk:
            send_message(contact, accumulated_response.strip())
            accumulated_response = ""
    # Send any remaining accumulated message at the end
    if accumulated_response.strip():
        send_message(contact, accumulated_response)

def poll_for_messages(contacts):
    global seen_messages
    
    # Ignore the last message that's there
    seen_messages = [get_latest_imessage_from_contact(contact) for contact in contacts]
    
    verbose_print("Starting to poll for messages...")
    while True:
        for contact in contacts:
            verbose_print("Checking for new message...")
            latest_message = get_latest_imessage_from_contact(contact)
            if latest_message not in seen_messages:
                print(f"\n\n> {latest_message}\n")
                seen_messages.append(latest_message)
                process_message(contact, latest_message)
            print("\n(Listening)")

        time.sleep(4)

def signal_handler(sig, frame):
    print('\n\nExiting...\n')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    print("\n●\n\nWelcome to The Open Interpreter iMessage Server.\n\nPress CTRL-C to exit.\n")
    time.sleep(1)
        
    contacts = get_last_five_contacts()
    print("Last 5 iMessage contacts:\n\n" + '\n'.join(f"- {contact}" for contact in contacts))
    
    input_contacts = input("\nEnter trusted contacts to control Open Interpreter, separated by commas:\n\n")
    selected_contacts = input_contacts.split(',')
    selected_contacts = [contact.strip() for contact in selected_contacts]
    
    print(f"\n\n● Now listening for messages from: {selected_contacts} ...\n")
    poll_for_messages(selected_contacts)

if __name__ == "__main__":
    main()
