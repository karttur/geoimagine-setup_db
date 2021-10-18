'''
Created on 31 feb. 2018
Modified on 31 dec 2020 (changed to json instead of xml as input)
Last update 18 Oct 2021

@author: thomasgumbricht
'''

# Standard library imports

from os import path

# Third party imports

from base64 import b64encode

import netrc

# Package application imports

from geoimagine.setup_db import PGsession 
# Alternatively use from setup_db import *

def DbConnect(db):
    '''
    '''
    # the HOST must exist in the .netrc file in the users home directory
    HOST = 'karttur'
    
    # Retrieve login and password from the .netrc file
    secrets = netrc.netrc()
    
    # Authenticate username, account and password 
    username, account, password = secrets.authenticators( HOST )
    
    # Encode the password before sending it
    password = b64encode(password.encode())

    # Create a query dictionary for connecting to the Postgres server  
    query = {'db':db, 'user':username, 'pswd':password}
    
    return query

def SetUpProdDb(prodDB):
    '''
    Create production database (db)
    '''
    
    # Get the user and password for connecting to the db, login to the default cluster postgres
    query = DbConnect('postgres')
    
    # Connect to the Postgres Server
    iniSession = PGsession(query)
    
    # Set the name of your production database( db)
    prodDbD = {'dbname':prodDB}
    
    # Select the current (cluster) db
    iniSession.cursor.execute("SELECT current_database()")
    
    # Get the results from the SELECT statement
    record = iniSession.cursor.fetchone()
    
    # Print Current (cluster) db
    print ('    Current database', record[0])
    
    # Select the logged in user
    iniSession.cursor.execute("SELECT user")
    
    # Get the results from the SELECT statement
    record = iniSession.cursor.fetchone()
    
    # Print Current user
    print ('    User', record[0])
    
    # Select all databases in the cluster db
    iniSession.cursor.execute("SELECT datname FROM pg_database;")
    
    # Get the results from the SELECT statement
    records = iniSession.cursor.fetchall()
    
    # Convert the retrieved records to a simple list
    dbL = [item[0] for item in records]
   
    # Print the list of all databases in the cluster
    print ('    Databases', dbL)

    # Check if your required production db is in the list
    if not prodDbD['dbname'] in dbL:
        
        # The requested production db does not exists
        
        printstr = '    Creating database: %s' %( prodDbD['dbname'])
        
        

        #Import the psycopg extension that allows you to create a new db
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        #Invoke the connection with the extension
        iniSession.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        #Create your production db
        iniSession.cursor.execute("CREATE DATABASE %(dbname)s;" %prodDbD)
        
    else:
        
        printstr = '    Database %s already exists' %( prodDbD['dbname'])
        
    print (printstr)
    
def SetupSchemasTables(projFPN,db):
    '''
    Setup schemas and tables
    '''
        
    # Get the full path to the project text file
    dirPath = path.split(projFPN)[0]
    
    # Open and read the text file linking to all json files defining the project
    with open(projFPN) as f:
        
        jsonL = f.readlines()
    
    # Clean the list of json objects from comments and whithespace etc    
    jsonL = [path.join(dirPath,x.strip())  for x in jsonL if len(x) > 10 and x[0] != '#']
    
    # Get the user and password for connecting to the db
    query = DbConnect(db)
    
    # Connect to the Postgres Server
    session = PGsession(query)
    
    # Loop over all json files and create Schemas and Tables
    for jsonObj in jsonL:
        
        print ('    jsonObj',jsonObj)
        
        session.ReadRunJson(jsonObj)
        
    # Close the db connection   
    session._Close()

if __name__ == "__main__":

    '''
    This module should only be run at the very startup of building the Karttur GeoImagine framework.
    To run, remove the comment "#prodDB" and set the name of your production DB ("YourProdDB")
    '''
    
    # Set the name of the productions db cluster
    # prodDB = 'YourProdDB' #'e.g. postgres or geoimagine
    prodDB = 'geoimagine'

    '''
    SetUpProdDb creates an empty Postgres database.
    '''
    SetUpProdDb(prodDB)

    '''
    SetupSchemasTables creates schemas and tables from json files, with the relative path to the
    json files given in the plain text file "projFPN".
    '''
    projFPN = path.join('doc','db_karttur_setup_20211018.txt')
    #SetupSchemasTables(projFPN,prodDB)

    '''
    #db_karttur_dbusers_YYYYMMDDX.xml adds db users for handling connections to postgres db
    '''
    projFPN = path.join('doc','db_karttur_dbusers_20211018.txt')
    SetupSchemasTables(projFPN,prodDB)

