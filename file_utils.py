import os
import shutil
from colors import Colors
import logging
import time

def delete_file(file_path):
    try:
        os.remove(file_path)
        logging.info(f"Deleted file {os.path.basename(file_path)}.")
        print(f"{Colors.OKGREEN}Deleted file {os.path.basename(file_path)}.{Colors.ENDC}")
    except Exception as e:
        logging.error(f"Error deleting file {os.path.basename(file_path)}: {e}")
        print(f"{Colors.FAIL}Error deleting file {os.path.basename(file_path)}: {e}{Colors.ENDC}")

def move_file(src_path, dest_path):
    try:
        shutil.move(src_path, dest_path)
        logging.info(f"Moved file from '{src_path}' to '{dest_path}'")
        print(f"{Colors.OKGREEN}Moved file from '{src_path}' to '{dest_path}'{Colors.ENDC}")
    except FileNotFoundError:
        logging.warning(f"File {src_path} was not found when attempting to move.")
        print(f"{Colors.WARNING}File {src_path} was not found when attempting to move.{Colors.ENDC}")
    except Exception as e:
        logging.error(f"Error moving file {src_path}: {e}")
        print(f"{Colors.FAIL}Error moving file {src_path}: {e}{Colors.ENDC}")

def delete_inactive_folders(folder_activity, timeout, exclude_path=None):
    current_time = time.time()
    keys_to_delete = []
    for folder, last_active in folder_activity.items():
        if folder == exclude_path or current_time - last_active <= timeout:
            continue
        keys_to_delete.append(folder)
    
    for key in keys_to_delete:
        shutil.rmtree(key, ignore_errors=True)
        del folder_activity[key]
        logging.info(f"Deleted inactive folder {key}.")
        print(f"{Colors.OKGREEN}Deleted inactive folder {key}.{Colors.ENDC}")