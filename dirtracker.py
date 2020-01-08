import os
import time
import core
import getpass
from utils import write_to_log
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

observer_paused = False

#---------------------------------------------------------
# Upload the specified file to the S3 bucket.
# Takes care of session, client, authentication, and upload.
#---------------------------------------------------------
def upload_file_to_S3(event):

    global observer_paused, aws_session, bucket

    # Don't respond to events if paused flag is true.
    # Make sure to only upload files and ignore directories.
    if observer_paused or not os.path.isfile(event.src_path):
        return

    # Unify folder names. (username replaced with placeholder)
    s3_key = event.src_path.replace(getpass.getuser(), core.user_placeholder).replace('\\', '/')

    s3_client = aws_session.resource('s3')

    s3_client.meta.client.upload_file(event.src_path, bucket, s3_key)

    write_to_log('Uploaded file ' + s3_key)

#---------------------------------------------------------
# Tracks file changes in the specified directories.
#---------------------------------------------------------
def track_directories(directories, session, bucket_name):

    global aws_session, bucket
    aws_session = session
    bucket = bucket_name

    observer = Observer()

    # Create event handler and set the function to call when event occurs.
    event_handler = FileSystemEventHandler()
    event_handler.on_created = upload_file_to_S3


    # Schedule the observer to monitor every directory in the config file.
    for directory in directories:
        observer.schedule(event_handler, directory, recursive=True)
        write_to_log('Scheduled observer for ' + directory)

    # Start the observer.
    observer.start()

    try:

        write_to_log('Beginning to wait for events.')

        # Constantly wait for events.
        while True:
            time.sleep(1)

    # Stop when user presses Ctrl + C.
    except KeyboardInterrupt:
        write_to_log('Stopping observers...')
        observer.stop()
        observer.join()
        write_to_log('Stopped observers.')