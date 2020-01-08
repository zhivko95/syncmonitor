import dirtracker
import subprocess
import core
import time
import getpass
from utils import write_to_log
from datetime import datetime

#---------------------------------------------------------
# Checks if the bucket contents have been updated.
#---------------------------------------------------------
def sync_monitor(session, config):

    # Create the initial locally stored folder update times.
    last_local_update_time = dict()
    for directory in config['folders']:
        last_local_update_time[directory] = datetime(1000, 1, 1, 0, 0, 0)

    #Get a new DynamoDB resource
    db_client = session.client('dynamodb')

    # If the update times table exists, check all of the entries.
    db_folder_update_times = dict()

    # Get the last update time for each folder from the table.
    while True:
        
        write_to_log('Checking folder update times.')

        for folder_path in config['folders']:

            try:

                # Unify folder names.
                unified_folder_path = folder_path.replace(getpass.getuser(), core.user_placeholder).replace('\\', '/')

                db_folder_update_times[folder_path] = datetime.strptime(db_client.get_item(TableName=config['dynamodb_table_name'], Key={'FolderName': {'S': unified_folder_path.replace(' ', '+')}})['Item']['LastUpdate']['S'], '%Y-%m-%d %H:%M:%S')

                # If we updated before the last update time stored in the db.
                if(db_folder_update_times[folder_path] > last_local_update_time[folder_path]):

                    write_to_log('Need to update folder ' + folder_path)
                    #print('--------------------------------------')

                    #Run batch file with aws cli sync.
                    with open('sync.bat', 'w') as cli_file:

                        bucket_path = config['bucket'] + '/' + unified_folder_path
                        cli_file.write('aws s3 sync "s3://%s" "%s"' %(bucket_path, folder_path))

                    # Pause observer while we sync directory.
                    dirtracker.observer_paused = True

                    # Run sync batch file hidden.
                    SW_HIDE = 0
                    info = subprocess.STARTUPINFO()
                    info.dwFlags = subprocess.STARTF_USESHOWWINDOW
                    info.wShowWindow = SW_HIDE
                    p = subprocess.Popen('sync.bat', startupinfo=info)
                    p.communicate()

                    dirtracker.observer_paused = False

                    # Update last updated time for the folder in the local dict.
                    last_local_update_time[folder_path] = db_folder_update_times[folder_path]

                    #print('--------------------------------------')
                    write_to_log('Folder ' + folder_path + ' updated.')
            
                else:
                    write_to_log('Do not need to update ' + folder_path)
        
            # If update times table does not exist, create it.
            except db_client.exceptions.ResourceNotFoundException:
                    
                db_client.create_table(AttributeDefinitions=[{'AttributeName': 'FolderName', 'AttributeType': 'S'}], \
                                                                TableName=config['dynamodb_table_name'], KeySchema=[{'AttributeName': 'FolderName', 'KeyType': 'HASH'}], \
                                                                    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})

                write_to_log('Update time table not found, created new table.')

            # Most likely means that table was newly created and has no items.
            except KeyError:

                write_to_log('Folder ' + folder_path + ' not found in db table. Either typo or db table is empty.')

        # Delay timer.
        write_to_log('Finished checking folders. Sleeping for ' + str(config['sync_check_freq']) + ' seconds.')
        time.sleep(config['sync_check_freq'])
