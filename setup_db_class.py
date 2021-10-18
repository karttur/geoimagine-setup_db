'''
Created on 21 feb. 2018
Last update 18 Oct 2021

@author: thomasgumbricht

'db_setup_class' is used for creating database schemas and tables as defined in xml files.
'db_setup_class' contains a single class 'PGsession'. 
The initiating expects a query dictionary with 
database [db], user [user] and password [pswd] with [pswd] encoded using the base64 package
'''

# Standard library imports

import json

import psycopg2

from sys import exit

# Third party imports

from base64 import b64decode

from pprint import pprint

       
class Struct(object):
    ''' Recursive class for building project objects
    '''
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

class Params:
    '''
    classdocs
    '''
    def __init__(self, jsonFPN):
        '''
        '''
        
        # Read the initial (default) parameters
        
        defaultjsonFPN = '/Users/thomasgumbricht/Documents/geoimagine_default_thomasg.json' 
        
        iniParams = self._JsonParams (defaultjsonFPN) 
                        
        self.jsonParams = self._JsonParams (jsonFPN)
                
        # update userproject, fill in any default setting from the project default json
        self._UpdateProject(self.jsonParams, iniParams)
        
        # update processes, fill in any default setting from the project default json
        if 'process' in self.jsonParams and 'process' in iniParams:
            for p in self.jsonParams['process']:
                self._UpdateProject(p, iniParams['process'][0])
            
        #Convert jsaonParams for class attribtures
        self.params = Struct(self.jsonParams)
        
    def _UpdateProject(self, mainD, defaultD):
        '''
        '''

        d = {key: defaultD.get(key, mainD[key]) for key in mainD}
        
        for key in defaultD:
            if key not in d:
                mainD[key] = defaultD[key]
                                   
    def _JsonParams(self,path):
        '''
        '''
        
        # Opening JSON file 
        f = open(path,) 
                 
        # returns JSON object
        return json.load(f)
                                  
    def _GetDict(self):
        '''
        '''
        return self.jsonParams

class PGsession:
    """Connect to postgres server"""   
    def __init__(self, query):
        """Connect to selected database"""
        query['pswd'] = b64decode(query['pswd']).decode('ascii')
        conn_string = "host='localhost' dbname='%(db)s' user='%(user)s' password='%(pswd)s'" %query
        print ('conn_string',conn_string)
        self.conn = psycopg2.connect(conn_string)
        self.cursor = self.conn.cursor()
        
    def ReadRunJson(self, jsonObj):
        ''' Read and run json object
        '''
        params = Params(jsonObj)
        
        self.params = params.params
        
        # Get the processes as listed in the jsonObject
        for process in self.params.process:
            
            self.verbose = process.verbose
            
            self.delete = process.delete
            
            self.overwrite = process.overwrite
            
            if self.verbose > 1:
                
                print ('    process parameters:')
                pprint (vars(process))
                             
            if process.processid == 'createschema':
                
                self._CreateSchema(process.parameters.schema)  
                 
            elif process.processid == 'createtable':
                
                self._CreateTable(process.parameters.schema,process.parameters.table,process.parameters.command)
            
            elif process.processid == 'tableinsert':
                
                self._TableInsert(process.parameters.schema,process.parameters.table,process.parameters.command.columns,process.parameters.command.values)
            
            elif process.processid == 'tableupdate':
                
                self._TableUpdate(process.parameters.schema,process.parameters.table,
                                  process.parameters.command.where,process.parameters.command.columns,process.parameters.command.values)
            
            elif process.processid == 'grant':
                
                self._Grant(process.parameters.command)
                
            else:
                exitstr =  'Initial command not found in initiate.initialize', process.processid
                exit(exitstr)
          
    def _CreateSchema(self,schema):
        ''' Create schema if it does not exist '''
        
        query = {'schema':schema}
        
        if self.verbose:
            
            sql = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '%(schema)s';"%query
                    
            print ('    ',sql)
        
        self.cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = '%(schema)s';"%query)
        
        record = self.cursor.fetchone()
        
        if record != None:
                
            if self.overwrite or self.delete:
                
                if self.verbose:
            
                    sql = "DROP SCHEMA %(schema)s" %query
                    
                    print ('    ',sql)
     
                self.cursor.execute("DROP SCHEMA %(schema)s" %query) 
            
                self.conn.commit()
                
                if self.delete:
                    
                    return
            else:
                
                return
   
        if self.verbose:
                
            infostr = '    Creating schema %s' %(schema)
                
            print (infostr)

        self.cursor.execute("CREATE SCHEMA %(schema)s;"  %query)
            
        self.conn.commit()

    def _CreateTable(self,schema,table,cmd):  
        ''' Create, overwrite or drop table ''' 
             
        cmd = ",".join(cmd)

        query = {'schema':schema,'table':table,'cmd':cmd}
        
        if self.verbose:
            
            sql = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '%(schema)s' AND table_name = '%(table)s');"%query
                    
            print ('    ',sql)
        
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '%(schema)s' AND table_name = '%(table)s');"%query)
       
        record = self.cursor.fetchone()
        
        #self.cursor.execute("SET search_path TO " + schema)

        if record[0]:
            
            if self.overwrite or self.delete:
                
                if self.verbose:
            
                    sql = "DROP TABLE %(schema)s.%(table)s;" %query
                    
                    print ('    ',sql)

                self.cursor.execute("DROP TABLE %(schema)s.%(table)s;" %query) 
            
                self.conn.commit()
                
                if self.delete:
                    
                    return
            else:
                
                return
            
        if self.verbose:
                            
            sql = "CREATE TABLE %(schema)s.%(table)s ( %(cmd)s );" %query
                
            print ('    ',sql)
 
        self.cursor.execute("CREATE TABLE %(schema)s.%(table)s ( %(cmd)s );" %query)
        
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
            
    def _TableInsert(self,schema,table,columns,valueL):
        ''' Insert, replace of delete records in schema table ''' 
        
        query = {'schema':schema,'table':table}
        
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '%(schema)s' AND table_name = '%(table)s');"%query)
        
        record = self.cursor.fetchone()
        
        if not record[0]:
        
            exitstr = 'Schema %s Table %s does not exist' %(schema,table)
            
            exit(exitstr)
               
        tablekeys = self._GetTableKeys(table)
        
        keycols = []
        
        for item in tablekeys:
            
            keycols.append(str(item[0].lower())) 
                                       
        for values in valueL:
            
            askqueryL = []
            
            for x, item in enumerate(columns):
                
                for key in keycols:
                    
                    if str(item.lower().strip()) == str(key.lower().strip()):
                        
                        askqueryL.append('%s = %s' %(item, values[x]))
                        
            whereSql = " AND ".join(askqueryL)  
            
            query = {'schema':schema, 'table':table, 'where': whereSql} 
            
            if self.verbose:
                
                sql = "SELECT * FROM %(schema)s.%(table)s WHERE %(where)s;" %query
                
                print ('    ',sql)
                        
            self.cursor.execute("SELECT * FROM %(schema)s.%(table)s WHERE %(where)s;" %query)    
            
            record = self.cursor.fetchone()
            
            if record != None:
                
                if self.overwrite or self.delete:
                    
                    if self.verbose:
                
                        sql = "DELETE FROM %(schema)s.%(table)s WHERE %(where)s;" %query
                        
                        print ('    ',sql)

                    self.cursor.execute("DELETE FROM %(schema)s.%(table)s WHERE %(where)s;" %query) 
                
                    self.conn.commit()
                    
                    if self.delete:
                        
                        return
                else:
                    
                    return
                        
            queryinsert = {'schema':schema, 'table':table, 'cols': ",".join(columns), 'vals':",".join(values)}
            
            if self.verbose:
            
                sql = "INSERT INTO %(schema)s.%(table)s (%(cols)s) VALUES (%(vals)s);" %queryinsert
                
                print ('    ',sql)

            self.cursor.execute("INSERT INTO %(schema)s.%(table)s (%(cols)s) VALUES (%(vals)s);" %queryinsert)
            
            self.conn.commit()
                
    def _TableUpdate(self, schema, table, where, columns, values):
        ''' Update records in schema table ''' 
        
        query = {'schema':schema,'table':table}
        
        self.cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '%(schema)s' AND table_name = '%(table)s');"%query)
        
        record = self.cursor.fetchone()
        
        if not record[0]:
        
            print ( 'WARNNG: Can not update; Schema %s Table %s does not exist' %(schema,table) )
            
            return
                
        query = {'schema':schema, 'table':table, 'where': where} 

        self.cursor.execute("SELECT * FROM %(schema)s.%(table)s WHERE %(where)s;" %query) 
           
        record = self.cursor.fetchone()
        
        if record == None:
            
            errorstr = 'Can not update non-existing record'
            
            exit(errorstr)
            
        query = {'schema':schema,'table':table, 'cols': ",".join(columns), 'vals':",".join(values), 'where':where}
        
        if self.verbose:
            
            sql = "UPDATE %(schema)s.%(table)s SET (%(cols)s) = (%(vals)s) WHERE %(where)s;" %query
            
            print ('    ',sql)
        
        self.cursor.execute("UPDATE %(schema)s.%(table)s SET (%(cols)s) = (%(vals)s) WHERE %(where)s;" %query)
        
        self.conn.commit()
                
    def _Grant(self,command):
        ''' Grant user rights
        '''
        
        cmd = "\n".join(command)
             
        self.cursor.execute(cmd)
                
        self.conn.commit()                    
        
    def _Close(self):
        
        self.cursor.close()
        
        self.conn.close()
        
