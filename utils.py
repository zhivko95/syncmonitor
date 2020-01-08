import yaml
import os
import boto3
from datetime import datetime

#---------------------------------------------------------
# Read configuration file and store stuff in variables.
#---------------------------------------------------------
def get_config():

    config = False

    # Load yaml file contents into a dictionary of config parameters.
    while not config:

        try:

            with open('config.yaml', 'r') as config_file:
                config = yaml.load(config_file, Loader=yaml.FullLoader)
                write_to_log('Loaded config from config.yaml.')
                return config
        
        except FileNotFoundError:
            write_to_log('Config file (config.yaml) not found, creating new default version.')

            default_config_lines = {'folders': ['C:\\Users\\Public\\Documents'], 'dynamodb_table_name': 'SyncUpdateTimes', 'sync_check_freq': 600, 'bucket': 'awsbackups1223', 'sync': True, 'region': 'ca-central-1'}

            with open('config.yaml', 'w') as config_file:
                yaml.dump(default_config_lines, config_file)

#---------------------------------------------------------
# Read credentials from file and store in a dictionary.
#---------------------------------------------------------
def get_credentials(config):

    try:

        with open('credentials.csv', 'r') as cred_file:

            headers = cred_file.readline().split(',')
            info = cred_file.readline().split(',')

            creds = dict(zip(headers, info))

        os.environ['AWS_ACCESS_KEY_ID'] = creds['Access key ID']
        os.environ['AWS_SECRET_ACCESS_KEY'] = creds['Secret access key']
        os.environ['AWS_DEFAULT_REGION'] = config['region']

        write_to_log('Retrieved credentials and set environment variables for AWS CLI.')

        return creds

    except FileNotFoundError:
        write_to_log('Credentials file (credentials.csv) not found.')
        sys.exit()

#---------------------------------------------------------
# Uses the given credentials to create a new boto3 session.
#---------------------------------------------------------
def get_session(creds, config):

    write_to_log('Started boto3 session.')

    return boto3.session.Session(aws_access_key_id=creds['Access key ID'], aws_secret_access_key=creds['Secret access key'], region_name=config['region'])

#---------------------------------------------------------
# Write the specified message to the application log file.
#---------------------------------------------------------
def write_to_log(msg):

    with open('log.txt', 'a') as log_file:
        log_file.write(str(datetime.now())[:-7] + ' || ' + msg + '\n')
