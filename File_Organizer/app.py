import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import sys

print(f'Env: {sys.prefix}')

with open('config.json', 'rb') as config:
    config_data = json.load(config)

extension_to_folder = config_data["extension_to_folder"]

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, dst_folder, logger):
        self.dst_folder = dst_folder
        self.logger = logger

    def create_if_not_exists(self, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)

    def on_created(self, event):
        if not event.is_directory:
            filename, file_extension = os.path.splitext(event.src_path)
            logging.info(f"Got new file - {filename}")
            file_extension = file_extension.lower()

            if file_extension in extension_to_folder:
                file_type = extension_to_folder[file_extension]
                logging.info(f"File has been classfied as: {file_type}.")
                base_folder = os.path.join(self.dst_folder, file_type)
                self.create_if_not_exists(base_folder)
                dst =  os.path.join(base_folder, os.path.basename(event.src_path))
                try:
                    shutil.move(event.src_path, dst)
                    self.logger.info(f"Moved {event.src_path} to {dst}.")
                except:
                    self.logger.warning(f"Failed to move file: {event.src_path}.")
            else:
                self.logger.info(f"{event.src_path} has an unsupported extension.")
                others_folder = 'others'
                dst = os.path.join(self.dst_folder, others_folder)
                self.create_if_not_exists(dst)
                shutil.move(event.src_path, dst)
                self.logger.info(f"Moved {event.src_path} to {others_folder}.")

def monitor_folder(folder_path):
    print(f"Started watching: {folder_path}.")
    log_folder = "./logs"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_filename = log_folder + "/log_" + time.strftime("%Y%m%d-%H%M%S") + ".log"

    logging.basicConfig(filename=log_filename, level=logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console_handler)

    logger = logging.getLogger()
    event_handler = NewFileHandler(folder_path, logger)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Operation halted")
    observer.join()

folder_path = config_data["watch_folder_path"] # Replace with the folder path which you want the app to monitor files.
if __name__ == '__main__':
    monitor_folder(folder_path)
