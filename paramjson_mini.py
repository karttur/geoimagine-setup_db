'''
Created on 22 Jan 2021

@author: thomasgumbricht
'''

# Standard library imports

import json
      
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

if __name__ == '__main__':

    jsonFPN = '/Users/thomasgumbricht/GitHub/geoimagine-setup_db/doc/xmlsql/general_schema_v80_sql.json'
    
    params = Params(jsonFPN)
    
