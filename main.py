import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import PATH_TO_WATCH, DESTINATION_FOLDER, NO_ARTIST_FOLDER, FLAC_FOLDER, LOG_FILE_PATH
from file_utils import delete_file, move_file, delete_inactive_folders
from audio_processing import check_id3, convert_flac_to_mp3
from colors import Colors

class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, destination_folder, no_artist_folder, flac_folder):
        self.destination_folder = destination_folder
        self.no_artist_folder = no_artist_folder
        self.flac_folder = flac_folder
        self.folder_activity = {}
        self.processed_files = set()  # Initialize the set at the global scope or within a class

    def on_created(self, event):
        if event.is_directory:
            print(f"{Colors.OKBLUE}Directory created: {event.src_path}{Colors.ENDC}")
            return
        file_path = event.src_path
        folder_path = os.path.dirname(file_path)
        self.folder_activity[folder_path] = time.time()
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in ['.jpg', '.jpeg', '.png', '.m3u']:
            delete_file(file_path)
            print(f"{Colors.FAIL}File {os.path.basename(file_path)} is not a compatible image or playlist file. Deleted.{Colors.ENDC}")
            return
        if file_extension == '.flac':
            convert_flac_to_mp3(file_path, PATH_TO_WATCH, self.processed_files)
            destination_path = os.path.join(self.flac_folder, os.path.basename(file_path))
            print(f"{Colors.OKGREEN}FLAC file {os.path.basename(file_path)} converted and moved to {self.flac_folder}.{Colors.ENDC}")
        else:
            destination_path = check_id3(file_path, self.no_artist_folder, self.destination_folder)
            print(f"{Colors.OKGREEN}File {os.path.basename(file_path)} moved based on ID3 tags.{Colors.ENDC}")
        move_file(file_path, destination_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=LOG_FILE_PATH, filemode='a')
    print(f"{Colors.OKBLUE}Starting file observer...{Colors.ENDC}")
    event_handler = FileMoverHandler(DESTINATION_FOLDER, NO_ARTIST_FOLDER, FLAC_FOLDER)
    observer = Observer()
    observer.schedule(event_handler, PATH_TO_WATCH, recursive=True)
    observer.start()
    timeout_value = 30
    try:
        while True:
            delete_inactive_folders(event_handler.folder_activity, timeout_value, PATH_TO_WATCH)
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
        print(f"{Colors.WARNING}Stopping observer...{Colors.ENDC}")
    observer.join()
    print(f"{Colors.OKGREEN}Observer stopped.{Colors.ENDC}")