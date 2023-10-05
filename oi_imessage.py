
from flask import Flask, jsonify
import sqlite3
import os
import interpreter
from multiprocessing import Process
import time
import tempfile

'''
This is very hacky but it seems to mostly work.

First, create a Mac OS user dedicated to Open Interpreter (or don't if you want to go full Yolo).
Log in to that account and then you'll also want to create an Apple ID for them — this enables outbound messages. Go ahead and text yourself to make sure it's working.
Make sure you have Open Interpreter and other libraries (see below) installed.
Update the two lines under # Hardcoded variables as appropriate.

On modern versions of Mac OS, you'll also have to:

* Give Terminal Full Disk Access. Open settings and search "Full Disk Access" and something should pop up. You'll have to restart Terminal for this to take effect.
* I also gave Full Disk Accesss to Tmux, but this isn't strictly necessary, it was just very annoying when I was trying to remoteley fix things.
* Under settings, it can also be helpful but probably not necessary to turn on remote login, especially if you're ssh'ing in.
* Save this file where you want open interpreter to "live" and then run python openinterpreter_via_imessage.py
* Save your OpenAI key as a universal variable (Open Interpreter is usually good at helping you do this) so you don't have to save it here.

The first time you run it, you might need to manually click OK in a few places, and you'll probably also want to have run open interpreter previously, but other then that just send the email address associated with open interpreter an iMessage and it should hopefully respond.

'''

# Update these two lines
DATABASE_PATH = '/Users/  << OI username on Mac goes here >> /Library/Messages/chat.db'
CONTACT_NAME_OR_PHONE = '555-555-5555'

# Consider updating these lines
POLLING_INTERVAL = 5  # in seconds
interpreter.auto_run = True  # Don't require user confirmation
interpreter.system_message += "You are interacting with a user via text message. You can't share files with them, and they'll likely be busy or distracted so try to make sure that you clearly give them the information they ask for in a concise way."
# interpreter.max_budget = 0.01 # 1 cent

app = Flask(__name__)
latest_message_id = None
open_interpreter_process = None

def run_open_interpreter(message):
    response_message = ""
    for chunk in interpreter.chat(message, stream=True):
        if 'message' in chunk:
            response_message += chunk['message']
    send_message(CONTACT_NAME_OR_PHONE, response_message)

def get_latest_imessage():
    global latest_message_id
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        curs = conn.cursor()
        curs.execute("SELECT ROWID, text FROM message ORDER BY date DESC LIMIT 1;")
        last_message_data = curs.fetchone()
        conn.close()
        
        if last_message_data and (latest_message_id is None or last_message_data[0] > latest_message_id):
            latest_message_id = last_message_data[0]
            return last_message_data[1]
        
    except sqlite3.OperationalError as e:
        print(f"SQLite Error: {e}")
    return None

def send_message(contact, message):
    try:
        # Escape special characters to make the string compatible with AppleScript
        escaped_message = message.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "\\r")
        
        # Create a temporary file to store the AppleScript
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.applescript') as f:
            f.write(f'''
            tell application "Messages"
                set targetBuddy to "{contact}"
                send "{escaped_message}" to buddy targetBuddy of (service 1 whose service type is iMessage)
            end tell
            ''')
            temp_filename = f.name

        # Execute the AppleScript
        os.system(f'osascript {temp_filename}')
        
        # Remove the temporary file
        os.remove(temp_filename)

    except Exception as e:
        print(f"Failed to send message: {e}")
        send_message(contact, "Failed to send the original message due to special characters.")


def poll_for_messages():
    global open_interpreter_process
    while True:
        time.sleep(POLLING_INTERVAL)
        latest_message = get_latest_imessage()
        if latest_message:
            if latest_message.strip().upper() in ["STOP", "CANCEL"]:
                if open_interpreter_process and open_interpreter_process.is_alive():
                    open_interpreter_process.terminate()
                    print("Terminated Open Interpreter process.")
                    send_message(CONTACT_NAME_OR_PHONE, "Operation cancelled.")
                continue

            open_interpreter_process = Process(target=run_open_interpreter, args=(latest_message,))
            open_interpreter_process.start()

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"})

if __name__ == '__main__':
    polling_process = Process(target=poll_for_messages)
    polling_process.start()
    app.run(port=5000)
