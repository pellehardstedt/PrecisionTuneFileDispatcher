import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from mutagen.easyid3 import EasyID3
from mutagen import MutagenError
import ffmpeg

class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, destination_folder, no_artist_folder, flac_folder):
        self.destination_folder = destination_folder
        self.no_artist_folder = no_artist_folder  # Folder for files with no artist
        self.flac_folder = flac_folder  # Folder for .flac files
        self.folder_activity = {}  # Track last activity time of folders

    def on_created(self, event):
        super(FileMoverHandler, self).on_created(event)
        if event.is_directory:
            return
    
        file_path = event.src_path
        folder_path = os.path.dirname(file_path)
        self.folder_activity[folder_path] = time.time()  # Update activity time
    
        file_extension = os.path.splitext(file_path)[1].lower()
        # Check and delete image and .m3u files
        if file_extension in ['.jpg', '.jpeg', '.png', '.m3u']:
            try:
                os.remove(file_path)
                print(f"{Colors.OKGREEN}Deleted file {os.path.basename(file_path)}.{Colors.ENDC}")                
                return
            except Exception as e:
                print(f"{Colors.WARNING}Error deleting file {os.path.basename(file_path)}: {e}{Colors.ENDC}")
                return
    
        # Separate handling for .flac files
        if file_extension == '.flac':
            process_flac_file(file_path, path_to_watch)
            destination_path = os.path.join(self.flac_folder, os.path.basename(file_path))
        else:
            # Use checkID3 for other file types
            destination_path = self.checkID3(file_path)
    
        cleaned_file_path = os.path.relpath(file_path, start=os.path.commonpath([file_path, self.destination_folder]))
        try:
            shutil.move(file_path, destination_path)
            print(f"{Colors.OKBLUE}Moved file from '{cleaned_file_path}' to '{destination_path}'{Colors.ENDC}")
        except FileNotFoundError:
            print(f"{Colors.WARNING}File {cleaned_file_path} was not found when attempting to move.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.WARNING}Error moving file {cleaned_file_path}: {e}{Colors.ENDC}")

    def checkID3(self, file_path):
        try:
            audio = EasyID3(file_path)
            if not audio.get('artist'):
                # If artist tag is empty or not present, move to no_artist_folder
                return os.path.join(self.no_artist_folder, os.path.basename(file_path))
        except MutagenError:
            # If file is not compatible with EasyID3, log and proceed
            print(f"{Colors.OKCYAN}File {os.path.basename(file_path)} is not a compatible audio file.{Colors.ENDC}")

        # Default destination if artist is present or file is not an audio file
        return os.path.join(self.destination_folder, os.path.basename(file_path))

def delete_inactive_folders(folder_activity, timeout=120):
    current_time = time.time()
    for folder, last_active in list(folder_activity.items()):
        if current_time - last_active > timeout:
            # Check if the folder is empty
            if not os.listdir(folder):
                try:
                    shutil.rmtree(folder)
                    print(f"{Colors.OKCYAN}Deleted folder {folder} due to inactivity.{Colors.ENDC}")
                    del folder_activity[folder]
                except Exception as e:
                    print(f"{Colors.WARNING}Error deleting folder {folder}: {e}{Colors.ENDC}")

def process_flac_file(input_flac, path_to_watch):
    # Extract the base name (without extension) from the input FLAC file
    base_name = os.path.splitext(os.path.basename(input_flac))[0]
    
    # Define the new folder name and create it inside path_to_watch
    new_folder_path = os.path.join(path_to_watch, base_name)
    os.makedirs(new_folder_path, exist_ok=True)
    
    # Define the output MP3 file path inside the new folder
    output_mp3 = os.path.join(new_folder_path, base_name + '.mp3')
    
    # Convert the FLAC file to MP3 in the new folder
    convert_flac_to_mp3(input_flac, output_mp3)

def convert_flac_to_mp3(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"{Colors.WARNING}Error: The file {input_path} does not exist.{Colors.ENDC}")
        return
    try:
        # Suppressing the output by capturing stdout and stderr
        ffmpeg.input(input_path).output(output_path).run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print(f"{Colors.WARNING}Error converting file: {e}{Colors.ENDC}")

if __name__ == "__main__":
    path_to_watch = "C:\\Users\\Pelle\\Documents\\Soulseek Downloads\\complete"
    destination_folder = "C:\\Users\\Pelle\\Music\\iTunes\\iTunes Media\\Automatically Add to iTunes"
    no_artist_folder = "C:\\Users\\Pelle\\Documents\\Soulseek Downloads\\no_artist"
    flac_folder = "C:\\Users\\Pelle\\Documents\\Soulseek Downloads\\flac"
    event_handler = FileMoverHandler(destination_folder, no_artist_folder, flac_folder)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()
    try:
        while True:
            delete_inactive_folders(event_handler.folder_activity)
            time.sleep(10)  # Check for inactive folders every 10 seconds
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# ANSI escape codes for colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename="C:\\Users\\Pelle\\Documents\\Soulseek Downloads\\import.log", 
                    filemode='a')