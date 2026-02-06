from datetime import datetime
import os
from config import LOG_DIRECTORY_PATH


def write_to_log(message="event", prefix="", print_datestamp=True):
    # Date strings
    if print_datestamp:
        datestamp = datetime.now().strftime("%m.%d.%Y")
    else:
        datestamp = ""

    timestamp = datetime.now().strftime("%H.%M.%S")

    # Filename
    fname = f"{prefix}-{datestamp}-log.txt"

    # Ensure log directory exists (recursive, no error if already there)
    os.makedirs(LOG_DIRECTORY_PATH, exist_ok=True)

    # Full path to log file
    log_path = os.path.join(LOG_DIRECTORY_PATH, fname)

    # Write log entry
    with open(log_path, "a") as fout:
        fout.write(f"{datestamp} - {timestamp}:   {message}\n\n")
