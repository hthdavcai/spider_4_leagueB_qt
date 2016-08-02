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
    path_variables = []

    def __init(self, URL='', items=[], tableName='', primaryKey='', task='', variables=[], path_variables=[]):
        self.URL = URL
        self.items = items
        self.tableName = tableName
        self.primaryKey = primaryKey
        self.task = task
        self.variables = variables
        self.path_variables = path_variables

    def __del__(self):
        print ''

    def __getURL__(self):
        return self.URL

    def __setURL__(self, value):
        self.URL = value

    def __getItems__(self):
        return self.items

    def __setItems__(self, value):
        self.items = value

    def __getTableName__(self):
        return self.tableName

    def __setTableName__(self, value):
        self.tableName = value

    def __getPrimaryKey__(self):
        return self.primaryKey

    def __setPrimaryKey__(self, value):
        self.primaryKey = value

    def __getTask__(self):
        return self.task

    def __setTask__(self, value):
        self.task = value

    def __getVariables__(self):
        return self.variables

    def __setVariables__(self, value):
        self.variables = value

    def __getChirdren__(self,):
        return self.chirdren

    def __setChirdren__(self, value):
        self.chirdren = value

    def __getPathVariables__(self):
        return self.path_variables

    def __setPathVariables__(self, path_variables):
        self.path_variables = path_variables
