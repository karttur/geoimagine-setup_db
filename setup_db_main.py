'''
Created on 21 feb. 2018

@author: thomasgumbricht
'''

from geoimagine.setup_db import PGsession
from base64 import b64encode
import netrc
from os import path

def SetUpProdDb(prodDB):
    '''
    Create production database(db)
    '''
    HOST = 'karttur'
    secrets = netrc.netrc()
    username, account, password = secrets.authenticators( HOST )
    #print ('username',username)
    password = b64encode(password.encode())

    #create a query dictionary for connecting to the Postgres server
    query = {'db':'postgres','user':username,'pswd':password}
    #Connect to the Postgres Server
    iniSession = PGsession(query)
    #Set the name of your production database(db)
    prodDbD = {'dbname':prodDB}
    #Select the current (cluster) db
    iniSession.cursor.execute("SELECT current_database()")
    #Get the results from the SELECT statement
    record = iniSession.cursor.fetchone()
    #Print Current (cluster) db
    print ('Current database', record[0])
    #Select the logged in user
    iniSession.cursor.execute("SELECT user")
    #Get the results from the SELECT statement
    record = iniSession.cursor.fetchone()
    #Print Current user
    print ('User', record[0])
    #Select all databases in the cluster db
    iniSession.cursor.execute("SELECT datname FROM pg_database;")
    #Get the results from the SELECT statement
    records = iniSession.cursor.fetchall()
    #Convert the retrieved records to a simple list
    dbL = [item[0] for item in records]
    #Print the list of all databases in the cluster
    print ('Databases', dbL)
    #Check if your required production db exists
    if not prodDbD['dbname'] in dbL:
        #Your production db does not exists
        printstr = 'Creating database: %s' %( prodDbD['dbname'])
        print (printstr)
        #Import the psycopg extension that allows you to create a new db
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        #Invoke the connection with the extension
        iniSession.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        #Create your production db
        iniSession.cursor.execute("CREATE DATABASE %(dbname)s;" %prodDbD)

def SetupSchemasTables(projFPN,db,verbose):
    '''
    Setup schemas and tables
    '''
    #Read the textfile with links to the xml files defining schemas and tables
    dirPath = path.split(projFPN)[0]
    with open(projFPN) as f:
        xmlL = f.readlines()
    # Remove whitespace characters like `\n` at the end of each line
    xmlL = [path.join(dirPath,x.strip())  for x in xmlL if len(x) > 10 and x[0] != '#']
    # Define the database connection
    HOST = 'karttur'
    secrets = netrc.netrc()
    username, account, password = secrets.authenticators( HOST )
    pswd = b64encode(password.encode())
    #create a query dictionary for connecting to the Postgres server
    query = {'db':db,'user':username,'pswd':pswd}
    #Connect to the Postgres Server
    session = PGsession(query)
    #Loop over all xml files and create Schemas and Tables
    for xml in xmlL:
        session.ReadSqxXml(xml,verbose)
    #close the db connection
    session._Close()

if __name__ == "__main__":

    prodDB = 'postgres'
    verbose = True
    '''
    This module should only be run at the very startup of building the Karttur Geo Imagine framework.
    To run, remove the comment "#prodDB" and set the name of your production DB ("YourProdDB")
    '''
    #prodDB = 'YourProdDB' #'postgres

    '''SetUpProdDb creates an empty Postgres database under the cluster postgres with the name "YourProdDB".'''
    #SetUpProdDb(prodDB)

    '''
    SetupSchemasTables creates schemas and tables from xml files, with the relative path to the
    xml files given in the plain text file "projFPN".
    '''
    #projFPN = 'doc/db_karttur_setup_20181116.txt'
    #SetupSchemasTables(projFPN,prodDB,verbose)

    '''
    #db_karttur_dbusers_YYYYMMDDX.xml adds db users for handling connections to postgres db
    '''
    #projFPN = 'doc/db_karttur_dbusers_20181116.txt'
    #SetupSchemasTables(projFPN,prodDB,verbose)

    '''
    #db_karttur_modregions_20181116.txt adds global default tiles to modis.region
    '''
    projFPN = 'doc/db_karttur_modregions_20181116.txt'
    SetupSchemasTables(projFPN,prodDB,verbose)
