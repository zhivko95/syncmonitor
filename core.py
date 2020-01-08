import dirtracker
import syncmonitor
import utils
import threading

user_placeholder = 'USER'

#---------------------------------------------------------
# Run order
#---------------------------------------------------------
if __name__ == '__main__':

    config = utils.get_config()
    credentials = utils.get_credentials(config)
    aws_session = utils.get_session(credentials, config)

    # Start the sync monitor in a separate daemon thread.
    sync = threading.Thread(target=syncmonitor.sync_monitor, args=(aws_session, config), daemon=True)
    sync.start()
    utils.write_to_log('Started sync monitor.')

    # Start monitoring for new files in directories using main thread.
    utils.write_to_log('Started directory trackers.')
    dirtracker.track_directories(config['folders'], aws_session, config['bucket'])