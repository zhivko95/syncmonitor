# syncmonitor
This Python application will monitor directories(from config file) for any newly created files(after the application has been started) and upload them to an S3 bucket(specified in config file). Using the defined time interval from the config file, the application will check whether any of the monitored folders need to be updated (synced) with the contents in the S3 bucket and proceed to do this using the AWS CLI(needs to be installed on the machine).

The software was created along with an installer which ensures that it executes on machine startup and runs in the background consistently. The main purpose of this software was to be used as a LAN sync folder but over the internet using S3 and other AWS features. Meaning that, running this software on multiple machines essentially creates a file sharing folder between all of them. Any file which is created on one computer will be uploaded to S3 and once all other machines perform their sync checks, the new file will be downloaded from S3 to every one of the other machines. 

# Requirements
- Boto3
- Watchdog
- AWS CLI installed

For full list of python modules, check the requirements.txt file.

# Getting Started

First, if you're planning to use the sync option of the application, make sure to have AWS CLI installed.

Second, create an IAM user with the name 'myapp' and no password. Download the credentials .csv file from the AWS Management Console and place it in the same folder as the source files.

Third, create a bucket which will be used to store new local files and later sync. Make sure to edit the bucket name in the config file.

To start the application, simply run core.py.

# Config File

The config file is used to specify some user options for the application. You can either create your own yaml config file or run the application once to create the defaul config file which can then be edited.

- ### Bucket
  The name of the S3 bucket which will be used to store files.

- ### DynamoDB Table Name
  Defines the name of the DynamoDB table which will be used to check if a folder sync is needed. Only use this parameter if you need to   change the table name. By default, the application will create its own DynamoDB table if none exists.

- ### Folders
  List of the local directories which should be monitored for new files.
  
- ### Region
  This option is used to defined the AWS region which will be used.
  
- ### Sync
  Defines whether the application should sync files from S3 or not. With this option as False, the application will only be uploading     files to S3 and acting more or less as a backup.(True = Sync ON, False = Sync OFF)
  
- ### Sync Check Frequency
  Used to define the time interval(seconds) to wait before checking if a folder sync is necessary. 

# Known Bugs/Concerns

- Syncing a folder with the S3 bucket will cause files with the same names to be overwritten in the local directory.
- Config file is loaded in only once(on application startup) and therefore config file changes require an application restart to take effect.
