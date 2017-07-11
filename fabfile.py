from fabric.api import *
from fabric.operations import *
from fabric.contrib.project import rsync_project
from fabric.contrib.files import exists
from pymongo import MongoClient

import sys, os

abspath = lambda filename: os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    filename
)

# --------------------------------------------
# DEV platform cofiguration
# --------------------------------------------

## run the command : fab dev deploy install

class FabricException(Exception):
    pass

def dev():
    print "Connecting to server"

    env.setup = True
    env.user = 'ubuntu'
    env.ubuntu_version = '16.04'
    env.warn_only = True
    env.development_env = 'dev'
    #env.password = 'ubuntu'         # if local machine then password of that machine
    env.key_filename = abspath('../*.pem')   # ec2 .pem filename with file location
    env.mongodb_service_config = abspath('mongodb.service')
    env.mongodb_config = abspath('mongod.conf')
    env.hosts = [
            'server_ip'
    ]
    env.mongo_script = 'runDB.py'
    env.db_path = 'db-folder'
    env.db_name = 'db-folder'
    env.db_user = 'db-folder'
    env.db_pwd = 'your db-password'      # your db-folder user's password

    env.graceful = False
    env.home = '/home/ubuntu'         # home dir location

    env.rsync_exclude = [
        '.git',
        '.gitignore',
        '*.pyc',
        '*.pem',
    ]
    return

def install():
    print 'Start installing Dev Platform'
    update()
    install_mongodb()
    install_pymongo()
    mongodb_config()
    running_db()

# update the system
def update():
    print 'Start updating the system'
    sudo('apt-get update')
    return

# upgrade the system
def upgrade():
    print 'Start upgrading the system'
    sudo('apt-get upgrade')
    return

# Install mongodb using apt
def install_mongodb():
    print 'Installing mongodb'
    sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927')
    sudo('echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list')
    update()
    sudo('apt-get install -y mongodb-org')
    print 'Finished setting up Mongodb'
    return

# configuring mongodb, put the systemd file and configuration file to the server
def mongodb_config():
   print 'configuring mongodb'
   default_config='/etc/systemd/system/mongodb.service'
   if exists(default_config):
       sudo('rm /etc/systemd/system/mongodb.service')
       print 'Deleted default config'

   print 'Install mongodb config service file'
   put('%s' % (env.mongodb_service_config), '/etc/systemd/system/', use_sudo=True)

   default_config='/etc/mongod.conf'
   if exists(default_config):
       sudo('rm /etc/mongod.conf')
       print 'Deleted default mongo config for login and security'
   print 'Install mongodb config file for security and remote login'
   put('%s' % (env.mongodb_config), '/etc/', use_sudo=True)
   sudo('systemctl daemon-reload')
   sudo('systemctl restart mongodb')
   return

# Install pymongo
def install_pymongo():
    update()
    print('Installing pymongo')
    sudo("apt-get install -y python-pymongo")
    print('Finished Installing PyMongo')
    return

# put the pymongo script to the home dir to create db, user and restore the db
def running_db():
    put('%s' % (env.mongo_script))
    run('python %s' % (env.mongo_script))
    run('mongorestore -d %s /home/ubuntu/%s' %(env.db_name,env.db_path))
    print('Restored the db successfully...')
    sudo('sed -i "s/disabled/enabled/g" /etc/mongod.conf')
    print('Enabled mongodb authentication...')
    sudo('systemctl restart mongodb')
    return

def sync_code_base():
    print 'Syncing code base'
    rsync_project(env.home, abspath(env.db_path) + '*', exclude=env.rsync_exclude, delete=True, default_opts='-rvz')
    return

def deploy():
    sync_code_base()
    print('code base synced successfully...')

##################################################################################################
############FABRIC SCRIPT END##################
##################################################################################################
