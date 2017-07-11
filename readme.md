# mongodb deployment using fabric and pymongo #

We are going to create a fabric file which will deploy the mongodb to the Internet. To do this, we should have to have an idea about fabric.

Fabric is a Python library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks. It provides a basic suite of operations for executing local or remote shell commands (normally or via sudo) and uploading/downloading files, as well as auxiliary functionality such as prompting the running user for input, or aborting execution.

'''Task-1:'''
First, clone the repo and you need to backup the db( or download from s3 then unzip db ) and place it to the repo directory where you cloned. As example, in our case "db-folder" is the backed up directory.

'''Task-2:'''
Goto the fabric file and take a look at the ```dev()``` function. In this function there are some environment variables which defines the database information.

```
env.mongo_script = 'runDB.py'
env.db_path = 'db-folder'
env.db_name = 'db-folder'
env.db_user = 'db-folder'
env.db_pwd = 'your db-folder password'
```

Here in this snippet, the ```env.mongo_script``` variable contains a script which will create the database and user with username, password and db-roles. Here is the code:
```
from pymongo import MongoClient

client = MongoClient('localhost:27017')
db = client.db-folder
coll = db.dataset
db.add_user('db-folder', 'db-password', roles=["readWrite", "dbAdmin"])
```

The other environment variables like ```env.db_path```, ```env.db_name```, ```env.db_user``` and ```env.db_pwd``` contains the value of database path (/home/ubuntu/db-folder), name of database, username and password.

'''Task-3:'''
In the ```install()``` function firstly, the system will be updated then install mongodb using apt sources. In the ```mongodb_config()``` function, mongodb systemd file path is specified. If the path exists then it'll remove the file and upload mongodb.service systemd file. Here is the snippet:
```
def mongodb_config():
   print 'configuring mongodb'
   default_config='/etc/systemd/system/mongodb.service'
   if exists(default_config):
       sudo('rm /etc/systemd/system/mongodb.service')
       print 'Deleted default config'

   print 'Install mongodb config service file'
   put('%s' % (env.mongodb_service_config), '/etc/systemd/system/', use_sudo=True)
```
The next task of this function is to specify the mongodb configuration file path. It removes the file if exists and upload the local ```mongod.conf``` file from the repo directory. Here is the snippet:
```
def mongodb_config():
  default_config='/etc/mongod.conf'
  if exists(default_config):
    sudo('rm /etc/mongod.conf')
    print 'Deleted default mongo config for login and security'
  print 'Install mongodb config file for security and remote login'
  put('%s' % (env.mongodb_config), '/etc/', use_sudo=True)
  sudo('systemctl daemon-reload')
  sudo('systemctl restart mongodb')
  return
```

Now, the ```install_pymongo()``` function installs pymongo so that the ```runDB.py``` can run perfectly on the server. The ```running_db()``` function first upload the script to the home directory and run the script. Then restore the database using ```mongorestore``` command and enabled the authentication by editing the ```/etc/mongod.conf``` file and then restart the mongodb service.

Lastly, the ```sync_code_base()``` function upload the database to the server's home directory which is called in the ```deploy()``` function.
