
import os

LOGDIR="/root/basementbot/logs/"
EXT=".txt"
def logfile(name): return LOGDIR + name

# Logs are in the format:
# mm/dd/yyyy hh:mm:ss <username> (<nickname>) said "<message>" (path: <channel_id>/<message_id>)
#
def parse_log(log:str):
    """
    Will parse a given log string and return a dictionary with the following keys:
     - Timestamp
     - Username
     - Nickname
     - Message
     - Path
    """
    # Split the log into its parts
    parts = log.split(" ")
    print(parts)
    # Get the timestamp
    timestamp = " ".join(parts[0:2])
    # Get the username
    username = parts[2]
    # Get the nickname
    nickname = parts[3][1:-1]
    # Get the message
    message = parts[4][1:-1]
    # Get the path
    path = parts[6][:-1]
    # Return the dictionary
    return {
        "timestamp": timestamp,
        "username": username,
        "nickname": nickname,
        "message": message,
        "path": path
    }
    

def get_messages(username):
    for log in [filename for filename in os.listdir(LOGDIR) if filename.endswith(EXT) and filename!="master.txt"]:
        with open(logfile(log), "r") as f:
            for line in f:
                parsed=parse_log(line)
                if parsed["username"] == username:
                    yield parsed

for filename in os.listdir(LOGDIR):
    for message in get_messages("MR_H3ADSH0T"):
        print(message)
