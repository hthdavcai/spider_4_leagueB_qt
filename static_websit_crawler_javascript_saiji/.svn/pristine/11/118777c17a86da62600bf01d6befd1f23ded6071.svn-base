# -*- coding: utf-8 -*-
import json


class jsonDataDemo(json.JSONEncoder):      
    def default(self, o):
        return o.__dict__ 
        
    URL = ''
    items = []
    tableName = ''
    primaryKey = '' 
    task = ''
    variables = []
    chirdren = []
        
    def __init( self, URL='',items=[],tableName='',primaryKey='',task='',variables=[]):
        self.URL = URL
        self.items = items
        self.tableName = tableName
        self.primaryKey = primaryKey
        self.task = task
        self.variables = variables
    def __del__(self):
        print ''
    def __getURL__(self, URL):  
        return self.URL;  
    def __setURL__(self, URL, value):  
        self.URL = value;  
    def __getItems__(self, items):  
        return self.items;  
    def __setItems__(self, items, value):  
        self.items = value; 
    def __getTableName__(self,tableName):  
        return self.tableName;  
    def __setTableName__(self, tableName, value):  
        self.tableName = value;
    def __getPrimaryKey__(self, primaryKey):  
        return self.primaryKey;  
    def __setPrimaryKey__(self, primaryKey, value):  
        self.primaryKey = value;          
    def __getTask__(self, task):  
        return self.task;  
    def __setTask__(self, task, value):  
        self.task = value;
    def __getVariables__(self, variables):  
        return self.variables;  
    def __setVariables__(self, variables, value):  
        self.variables = value; 
    def __getChirdren__(self,chirdren):  
        return self.chirdren;  
    def __setChirdren__(self, value):  
        self.chirdren = value; 
