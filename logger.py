from datetime import datetime
import os
from config import LOG_DIRECTORY_PATH

def write_to_log(message="event", prefix="", print_datestamp=True):

    if print_datestamp:
        datestamp = datetime.now().strftime("%m.%d.%Y")
    else:
        datestamp = ""
        
    timestamp = datetime.now().strftime("%H.%M.%S")

    fname = f"{prefix}-{datestamp}-log.txt"

    path_str = f"{LOG_DIRECTORY_PATH}"

    if os.path.exists(path_str) == False:
        os.mkdir(path_str)

    os.chdir(path_str)
    if os.path.exists(fname):
        fout = open(fname, 'a')
        fout.write(f"{datestamp} - {timestamp}:   ")
        fout.write(f"{message}\n\n")
    else:
        fout = open(fname, 'w')
        fout.write(f"{datestamp} - {timestamp}:   ")
        fout.write(f"{message}\n\n")

    fout.close()