# DigitalLogbook
A digital alternative for log books in organizations. Built with python and flask framework. 
### Features 
1. Rfid support
2. Command line script to manage database.
3. Print support for log data
### Dependencies
1. pyserial
2. flask
3. mysql.connector
### Project structure 
`__init__.py`: Main file to drive application. Dependencies are flask framework.
```
serverIp = ("127.0.0.1",8999)
```
Replace your connection details in \_\_init\_\_.py file in the line above.

`database.py`: mysql database connection file for \_\_init\_\_.py. Replace below code with your database connection details.
```
host = '127.0.0.1'
user = 'root'
passwd = 'your_password'
db = 'logbook'
```

`manageDatabase.py`: script file to insert, delete and update database. 
1. Create New Room 
2. Delete Room
3. Show all Room
4. Add new Id map : New Rfid mapping with user Id
5. Delete Id map
6. Show Id number mapping
7. Initialize database

`rfid.py`: RfId Rest server that reads Rf Id from serial rf reader and post this data to client application (\_\_init\_\_.py)
```
serverIp = ("127.0.0.1",8999)
```
Replace your connection details in rfid.py file in the line above. Please sure the port of \_\_init\_\_.py and rfid.py are different. 

### Deployment 
After doing required configuration as mentioned in `Project Structure` section. Run `rfid.py` and `__init__.py` files. Please install required dependencies before running both the server scripts.

To install dependencies run:
```
pip install pyserial flask mysql.connector
```

To deploy application run:
```
python rfid.py
python __init__.py
```
