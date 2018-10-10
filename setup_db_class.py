'''
Created on 21 feb. 2018
@author: thomasgumbricht

'db_setup_class' is used for creating database schemas and tables as defined in xml files.
'db_setup_class' contains a single class 'PGsession'. 
The initiating expects a query dictionary with 
database [db], user [user] and password [pswd] with [pswd] encoded using the base64 package
'''

import psycopg2
from base64 import b64decode
from xml.dom import minidom
from sys import exit
from os import path

class PGsession:
    """Connect to postgres server"""   
    def __init__(self, query):
        """Connect to selected database"""
        query['pswd'] = b64decode(query['pswd']).decode('ascii')
        conn_string = "host='localhost' dbname='%(db)s' user='%(user)s' password='%(pswd)s'" %query
        self.conn = psycopg2.connect(conn_string)
        self.cursor = self.conn.cursor()
        
    def ReadSqxXml(self,xmlFPN,verbose):
        ''' Read XML file ''' 
        self.verbose = verbose
        dom = minidom.parse(xmlFPN)  
        if self.verbose:
            print ('    xmlfile', path.split(xmlFPN)[1])   
        processes = dom.getElementsByTagName('process')
        
        for process in processes:
            overwriteTag = process.getElementsByTagName('overwrite')
            if len(overwriteTag) == 0:
                self.overwrite = False
            else:
                self.overwrite = self._BoolTag(overwriteTag[0].firstChild.nodeValue )
            deleteTag = process.getElementsByTagName('delete')
            if len(deleteTag) == 0:
                self.delete = False
            else:
                self.delete = self._BoolTag(deleteTag[0].firstChild.nodeValue )
            processid = process.getAttribute('processid')
            #Get the parameters
            paramtag = process.getElementsByTagName('parameters')
            schema = paramtag[0].getAttribute('schema')
            
            if processid in ['createtable','tableinsert','tableupdate']:
                table = paramtag[0].getAttribute('table')
                if self.verbose:
                    print ('        %s %s %s' %(processid, schema, table) )
                command = process.getElementsByTagName('command')
                if not process in ['tableinsert','createschema']:
                    cmd = command[0].firstChild.nodeValue
                if processid in ['tableinsert','tableupdate']:
                    valueL = []
                    columns = command[0].getElementsByTagName('columns')
                    columnL = columns[0].firstChild.nodeValue.split(',')
                    values = command[0].getElementsByTagName('values')
                    for value in values:
                        valueL.append(value.firstChild.nodeValue.split(','))   
            elif processid == 'grant':
                user = paramtag[0].getAttribute('user')
                pswd = paramtag[0].getAttribute('pswd')
                command = process.getElementsByTagName('command')
                cmd = command[0].firstChild.nodeValue
            if processid == 'createschema':
                self._CreateSchema(schema)   
            elif processid == 'createtable':
                self._CreateTable(schema,table,cmd)
            elif processid == 'tableinsert':
                self._TableInsert(schema,table,columnL,valueL)
            elif processid == 'tableupdate':
                self._TableUpdate(schema,table,columnL,valueL,cmd)
            elif processid == 'grant':
                self._Grant(user,pswd,cmd)
            else:
                exitstr =  'Initial command not found in initiate.initialize', processid
                exit(exitstr)
        
    def _CreateSchema(self,schema):
        ''' Create schema if it does not exist '''
        query = {'schema':schema}
        self.cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = '%(schema)s';"%query)
        record = self.cursor.fetchone()
        if record == None:
            self.cursor.execute("CREATE SCHEMA %(schema)s;"  %query)
            self.conn.commit()
        self.conn.commit()

    def _CreateTable(self,schema,table,command):  
        ''' Create, overwrite or drop table '''      
        query = {'schema':schema,'table':table,'cmd':command}
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '%(schema)s' AND table_name = '%(table)s');"%query)
        record = self.cursor.fetchone()
        self.cursor.execute("SET search_path TO " + schema)
        if not record[0] and not self.delete:
            self.cursor.execute("CREATE TABLE %(table)s ( %(cmd)s );" %query)
            self.conn.commit()
        elif record[0] and (self.delete or self.overwrite):
            self.cursor.execute("DROP TABLE %(table)s;" %query)
            if self.overwrite:
                self.cursor.execute("CREATE TABLE %(table)s ( %(cmd)s );" %query)
                self.conn.commit()

    def _GetTableKeys(self,table):
        ''' Get table keys ''' 
        query = "SELECT \
                c.column_name, c.data_type \
                FROM \
                information_schema.table_constraints tc \
                JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name) \
                JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema AND tc.table_name = c.table_name AND ccu.column_name = c.column_name \
                where constraint_type = 'PRIMARY KEY' and tc.table_name = '%s';" %(table)
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records
            
    def _TableInsert(self,schema,table,columnL,valueL):
        ''' Insert, replace of delete records in schema table ''' 
        query = {'schema':schema,'table':table}
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '%(schema)s' AND table_name = '%(table)s');"%query)
        record = self.cursor.fetchone()
        if not record[0]:
            exitstr = 'Schema %s Table %s does not exist' %(schema,table)
            exit(exitstr)
        self.cursor.execute("SET search_path TO " + schema)
        
        tablekeys = self._GetTableKeys(table)
        keycols = []
        for item in tablekeys:
            keycols.append(str(item[0].lower()))    
        for values in valueL:
            askqueryL = []
            for x, item in enumerate(columnL):
                for key in keycols:
                    if str(item.lower().strip()) == str(key.lower().strip()):
                        askqueryL.append('%s = %s' %(item, values[x]))
            whereSql = " AND ".join(askqueryL)  
            query = {'table':table, 'where': whereSql} 
            self.cursor.execute("SELECT * FROM %(table)s WHERE %(where)s;" %query)    
            record = self.cursor.fetchone()
            if record == None:
                queryinsert = {'table':table, 'cols': ",".join(columnL), 'vals':",".join(values)}
                self.cursor.execute("INSERT INTO %(table)s (%(cols)s) VALUES (%(vals)s);" %queryinsert)
                self.conn.commit()
            elif self.overwrite:
                self.cursor.execute("DELETE FROM %(table)s WHERE %(where)s;" %query) 
                self.conn.commit()
                queryinsert = {'table':table, 'cols': ",".join(columnL), 'vals':",".join(values)}
                self.cursor.execute("INSERT INTO %(table)s (%(cols)s) VALUES (%(vals)s);" %queryinsert)
                print ("INSERT INTO %(table)s (%(cols)s) VALUES (%(vals)s);" %queryinsert)
                self.conn.commit()
            elif self.delete:
                self.cursor.execute("DELETE FROM %(table)s WHERE %(where)s;" %query) 
                self.conn.commit()
                
    def _TableUpdate(self,schema,table,columnL,valueL,cmd):
        ''' Update records in schema table ''' 
        query = {'schema':schema,'table':table}
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '%(schema)s' AND table_name = '%(table)s');"%query)
        record = self.cursor.fetchone()
        if not record[0]:
            print ( 'Warning: Can not update; Schema %s Table %s does not exist' %(schema,table) )
            return
        self.cursor.execute("SET search_path TO " + schema)
        for values in valueL:
            queryL = []
            for x, item in enumerate(columnL):
                queryL.append('%s = %s' %(item, values[x]))
            query = {'table':table, 'where': cmd} 

            self.cursor.execute("SELECT * FROM %(table)s %(where)s;" %query)    
            record = self.cursor.fetchone()
            if record == None:
                errorstr = 'Can not update non-existing record'
                exit(errorstr)
            query = {'table':table, 'cols': ",".join(columnL), 'vals':",".join(values), 'where':cmd}
            self.cursor.execute("UPDATE %(table)s SET (%(cols)s) = (%(vals)s) %(where)s;" %query)
            self.conn.commit()
            
    def _BoolTag(self,item):
        ''' Convert boolean variables from xml to python boolean (True or False)'''
        if item == '': 
            return False #i.e. no item given, assume False
        if item[0].lower() == 'n' or item.lower() == 'false':
            return False
        elif item[0].lower() == 'y' or item.lower() == 'true':
            return True
        else:
            exitstr = 'Can not resolve boolean node %(s)s' %{'s':item}
            exit(exitstr)
    
    def _Grant(self,user,pswd,cmd):
        
        userid = "'%s'" %(user.lower())
        print ('SELECT u.usename AS "User name" FROM pg_catalog.pg_user u WHERE u.usename = %s;' %(userid,))

        self.cursor.execute('SELECT u.usename AS "User name" FROM pg_catalog.pg_user u WHERE u.usename = %s;' %(userid,))
        record = self.cursor.fetchone()
        
        if record == None and not self.delete:
            self.cursor.execute("CREATE USER %s WITH PASSWORD '%s';"%(user.lower(), pswd))
            self.conn.commit()
            
            self.cursor.execute(cmd)
        elif record and self.delete:
            self.cursor.execute("DROP USER %s;" %(user.lower(), ))
            self.conn.commit()
        elif record:
            cmds = cmd.splitlines()
            for row in cmds:
                if len(row) > 25:
                    print ('row',row)
                    self.cursor.execute(row)
                    self.conn.commit()        

    def _Close(self):
        self.cursor.close()
        self.conn.close()