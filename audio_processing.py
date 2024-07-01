import os
from mutagen.easyid3 import EasyID3
from mutagen import MutagenError
import ffmpeg
from colors import Colors
import logging

def check_id3(file_path, no_artist_folder, destination_folder):
    try:
        audio = EasyID3(file_path)
        if not audio.get('artist'):
            print(f"{Colors.WARNING}No artist found in ID3 tags for {os.path.basename(file_path)}. Moving to no_artist_folder.{Colors.ENDC}")
            return os.path.join(no_artist_folder, os.path.basename(file_path))
    except MutagenError:
        print(f"{Colors.FAIL}File {os.path.basename(file_path)} is not a compatible audio file.{Colors.ENDC}")
        logging.info(f"File {os.path.basename(file_path)} is not a compatible audio file.")
    return os.path.join(destination_folder, os.path.basename(file_path))

def convert_flac_to_mp3(input_path, output_path):
    print(f"{Colors.OKBLUE}Starting conversion of {os.path.basename(input_path)} to MP3...{Colors.ENDC}")
    if not os.path.exists(input_path):
        print(f"{Colors.WARNING}The file {input_path} does not exist. Skipping conversion.{Colors.ENDC}")
        logging.warning(f"The file {input_path} does not exist.")
        return
    try:
        output_file_name = os.path.splitext(os.path.basename(input_path))[0] + '.mp3'
        full_output_path = os.path.join(output_path, output_file_name)

        ffmpeg.input(input_path).output(full_output_path).run(capture_stdout=True, capture_stderr=True)
        print(f"{Colors.OKGREEN}Successfully converted {os.path.basename(input_path)} to MP3.{Colors.ENDC}")
    except ffmpeg.Error as e:
        print(f"{Colors.FAIL}Error converting {os.path.basename(input_path)}: {e}{Colors.ENDC}")
        logging.error(f"Error converting file: {e}")