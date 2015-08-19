# -*- coding: utf-8 -*-
from entity.models import KnowledgeServer
from urlparse import urlparse

class KsUri(object):
    '''
    This class is responsible for the good quality of all URI generated by a KS
    in terms of syntax
    and coherent use throughout the whole application
    '''

    def __init__(self, uri):
        '''
        only syntactic check
        uu= urlunparse([o.scheme, o.netloc, o.path, o.params, o.query, o.fragment])
        uu= urlunparse([o.scheme, o.netloc, o.path, o.params, o.query, ''])
        così possiamo rimuovere il fragment e params query in modo da ripulire l'url ed essere più forgiving sulle api; da valutare
        '''
        self.uri = uri
        self.parsed = urlparse(self.uri)
        # I remove format options if any, e.g.
        # http://rootks.thekoa.org/entity/SimpleEntity/1/json/  --> http://rootks.thekoa.org/entity/SimpleEntity/1/json/
        self.clean_uri = uri
        # remove the trailing slash
        if self.clean_uri[-1:] == "/":
            self.clean_uri = self.clean_uri[:-1]
        # remove the format the slash before it and set self.format
        self.format = ""
        for format in Choices.FORMAT:
            if self.clean_uri[-(len(format)+1):].lower() == "/" + format:
                self.clean_uri = self.clean_uri[:-(len(format)+1)]
                self.format = format

        # I check whether it's structure i well formed according to the GenerateURIInstance method
        self.is_sintactically_correct = False
        # not it looks something like: http://rootks.thekoa.org/entity/SimpleEntity/1
        self.clean_parsed = urlparse(self.clean_uri)
        self.scheme = ""
        for scheme in Choices.SCHEME:
            if self.clean_parsed.scheme.lower() == scheme:
                self.scheme = self.clean_parsed.scheme.lower()
        self.netloc = self.clean_parsed.netloc.lower()
        self.path = self.clean_parsed.path
        if self.scheme and self.netloc and self.path:
            # the path should have the format: "/entity/SimpleEntity/1"
            # where "entity" is the module, "SimpleEntity" is the class name and "1" is the id or pk
            temp_path = self.path
            if temp_path[0] == "/":
                temp_path = temp_path[1:]
            # "entity/SimpleEntity/1"
            if temp_path.find('/'):
                self.namespace = temp_path[:temp_path.find('/')]
                temp_path = temp_path[temp_path.find('/')+1:]
                # 'SimpleEntity/1'
                if temp_path.find('/'):
                    self.class_name = temp_path[:temp_path.find('/')]
                    temp_path = temp_path[temp_path.find('/')+1:]
                    print(temp_path)
                    if temp_path.find('/') < 0:
                        self.pk_value = temp_path
                        self.is_sintactically_correct = True

    def search_on_db(self):
        '''
        Database check
        I do not put this in the __init__ so the class can be used only for syntactic check or functionalities
        '''
        if self.is_sintactically_correct:
            # I search the ks by netloc and scheme on ksm
            try:
                self.knowledge_server = KnowledgeServer.objects.using('ksm').get(scheme=self.schem, netloc=self.netloc)
                self.is_ks_known = True
            except:
                self.is_ks_known = False
            if self.is_ks_known:
                # I search for its module and class and set relevant flags
                pass
        self.is_present = False
        #I search on this database
        #  on URIInstance
            
class Choices():
    # in lower case as they are brought to lower before verification
    FORMAT = ['xml','json','html','browse']
    SCHEME = ['http','https']
