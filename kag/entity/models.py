# -*- coding: utf-8 -*-

from datetime import datetime
from random import randrange, uniform
from urlparse import urlparse

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Max, Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from lxml import etree

from userauthorization.models import KUser

import json
import urllib
import urllib2

import kag.utils as utils

from xml.dom import minidom
from email.encoders import encode_base64
import base64
from django.conf.urls import url

class CustomModelManager(models.Manager):
    '''
    Created to be used by SerializableSimpleEntity so that all classes that inherit 
    will get the post_save signal bound to model_post_save. The following decorator

    @receiver(post_save, sender=SerializableSimpleEntity)
    def model_post_save(sender, **kwargs):

    wouldn't work at all while it would work specifying the class name that inherits e.g. Workflow

    @receiver(post_save, sender=Workflow)
    def model_post_save(sender, **kwargs):

    '''
    def contribute_to_class(self, model, name):
        super(CustomModelManager, self).contribute_to_class(model, name)
        self._bind_post_save_signal(model)

    def _bind_post_save_signal(self, model):
        models.signals.post_save.connect(model_post_save, model)

def model_post_save(sender, **kwargs):
    if kwargs['instance'].URIInstance == "":
        try:
            kwargs['instance'].URIInstance = kwargs['instance'].generate_URIInstance()
            if kwargs['instance'].URIInstance != "":
                kwargs['instance'].save()
        except Exception as e:
            print (e.message)

class SerializableSimpleEntity(models.Model):
    '''
    URIInstance is the unique identifier of this SerializableSimpleEntity in this KS
    When a SerializableSimpleEntity gets imported from XML of from a remote KS a new
    URIInstance is generated using generate_URIInstance
    '''
    URIInstance = models.CharField(max_length=2000L)
    '''
    URI_imported_instance if the instance comes from XML (or a remote KS) this attribute
    stores the URIInstance as it is in the XML. Doing so I can update an instance with data
    from XML and still have a proper local URIInstance
    '''
    URI_imported_instance = models.CharField(max_length=2000L)
    '''
    URI_previous_version is the URIInstance of the previous version if 
    this record has been created with the new_version method.
    It is used when materializing to update the relationships from old to new records
    '''
    URI_previous_version = models.CharField(max_length=2000L, null=True, blank=True)
    objects = CustomModelManager()

    def SetNotNullFields(self):
        '''
        I need to make sure that every SerializableSimpleEntity can be saved on the database right after being created (*)
        hence I need to give a value to any attribute that can't be null
        (*) It's needed because during the import I can find a reference to an instance whose data is further away in the file
        then I create the instance in the DB just with the URIInstance but no other data
        '''
        for key in self._meta.fields:
            if (not key.null) and key.__class__.__name__ != "ForeignKey" and (not key.primary_key):
                if key.__class__.__name__ in ("CharField", "TextField"):
                    if key.blank:
                        setattr(self, key.name, "")
                    else:
                        setattr(self, key.name, "dummy")
                if key.__class__.__name__ in ("IntegerField", "FloatField"):
                    setattr(self, key.name, 0)
                if key.__class__.__name__ in ("DateField", "DateTimeField"):
                    setattr(self, key.name, datetime.now())
                
    # URI points to the a specific instance in a specific KS
    def generate_URIInstance(self):
        '''
        *** method that works on the same database of self ***
        This method is quite forgiving; there is no SimpleEntity? Then I use the class name and id_field="pk"
        there is no DataSetStructure? Then I use the app name
        '''
        try:
            # http://stackoverflow.com/questions/10375019/get-database-django-model-object-was-queried-from
            db_alias = self._state.db
            this_ks = KnowledgeServer.this_knowledge_server()

            # removing tail ".models"
            namespace = self.__class__.__module__[:-7]
            try:
                se = self.get_simple_entity(db_alias=db_alias)
                name = se.name
                id_field = se.id_field
                if se.dataset_structure != None:
                    namespace = se.dataset_structure.namespace
            except:
                name = self.__class__.__name__
                id_field = "pk"
            return this_ks.uri() + "/" + namespace + "/" + name + "/" + str(getattr(self, id_field))
        except Exception as es:
            print ("Exception 'generate_URIInstance' " + self.__class__.__name__ + "." + str(self.pk) + ":" + es.message)
            return ""
    
    def get_simple_entity(self, class_name="", db_alias='ksm'):
        '''
        *** method that works BY DEFAULT on the materialized database ***
        finds the instance of class SimpleEntity where the name corresponds to the name of the class of self
        '''
        logger = utils.poor_mans_logger()
        try:
            if class_name == "":
                return SimpleEntity.objects.using(db_alias).get(name=self.__class__.__name__)
            else:
                return SimpleEntity.objects.using(db_alias).get(name=class_name)
        except:
            logger.error('get_simple_entity - db_alias = ' + db_alias + ' - class_name self.__class__.__name__= ' + class_name + " " + self.__class__.__name__)
            
    def entities(self):
        '''
        Lists the entities associated whose entry point is the instance of class SimpleEntity corresponding to the class of self
        '''
        return DataSetStructure.objects.filter(entry_point__simple_entity=self.get_simple_entity())

    def foreign_key_attributes(self): 
        attributes = []
        for key in self._meta.fields:
            if key.__class__.__name__ == "ForeignKey":
                attributes.append(key.name)
        return attributes
                
    def related_manager_attributes(self): 
        attributes = ""
        for key in self._meta.fields:
            if key.__class__.__name__ == "RelatedManager":
                attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'
        return attributes
                
    def many_related_manager_attributes(self): 
        attributes = ""
        for key in self._meta.fields:
            if key.__class__.__name__ == "ManyRelatedManager":
                attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'
        return attributes
     
    def serialized_URI_SE(self, format='XML'):
        if format == 'XML':
            return ' URISimpleEntity="' + self.get_simple_entity().URIInstance + '" '  
        if format == 'JSON':
            return ' "URISimpleEntity" : "' + self.get_simple_entity().URIInstance + '" '
        
    def serialized_attributes(self, format='XML'):
        attributes = ""
        comma = ""

        for key in self._meta.fields: 
            if key.__class__.__name__ != "ForeignKey":
                value = getattr(self, key.name)
                if value is None:
                    value = ""
                if format == 'XML':
                    attributes += ' ' + key.name + '="' + str(value) + '"'  
                if format == 'JSON':
                    attributes += comma + '"' + key.name + '" : "' + str(value) + '"'
                    comma = ", "
                if format == 'HTML':
                    attributes += comma + '"' + key.name + '" : "' + str(value) + '"'
                    comma = "<br>"
        return attributes

    def shallow_dataset_structure(self, db_alias='default'):
        '''
        It creates an DataSetStructure, saves it on the database and returns it.
        The structure created is shallow e.g. it has no depth but just one node
        THE NEED: if a user wants to serialize a SimpleEntity without passing an DataSetStructure
        I search for an DataSetStructure with is_shallow=True; if I can't find it I create it and save it
        for future use
        '''
        try:
            se = DataSetStructure.objects.using(db_alias).get(entry_point__simple_entity=self.get_simple_entity(), is_shallow=True)
        except:
            se = DataSetStructure()
            se.is_shallow = True
            se.name = self.__class__.__name__ + " (shallow)"
            se.simple_entity = self.get_simple_entity()
            se.entry_point = self.shallow_structure_node(db_alias)
            se.save()
            se.URIInstance = se.generate_URIInstance()
            se.save(using=db_alias)
        return se 
        
    def shallow_structure_node(self, db_alias='default'):
        '''
        it creates an StructureNode used to serialize (to_xml) self. It has the SimpleEntity 
        and references to ForeignKeys and ManyToMany
        '''
        etn = StructureNode()
        etn.simple_entity = self.get_simple_entity() 
        etn.external_reference = False
        etn.is_many = False
        etn.save(using=db_alias)
        etn.child_nodes = []
        for fk in self.foreign_key_attributes():
            etn_fk = StructureNode()
            if getattr(self, fk) is None:
                # the attribute is not set so I can't get its __class__.__name__ and I take it from the model
                class_name = self._meta.get_field(fk).rel.model.__name__
                try:
                    etn_fk.simple_entity = self.get_simple_entity(class_name)
                except Exception as ex:
                    logger = utils.poor_mans_logger()
                    logger.error("shallow_structure_node class_name = " + class_name + " - " + ex.message)
            else:
                etn_fk.simple_entity = getattr(self, fk).get_simple_entity()
            etn_fk.external_reference = True
            etn_fk.attribute = fk
            etn_fk.is_many = False
            etn_fk.save(using=db_alias)
            etn.child_nodes.add(etn_fk)
        for rm in self.related_manager_attributes():
            # TODO: shallow_structure_node: implement self.related_manager_attributes case
            pass
        for mrm in self.many_related_manager_attributes():
            # TODO: shallow_structure_node: implement self.many_related_manager_attributes case
            pass
        etn.save(using=db_alias)
        return etn

    def serialize(self, etn=None, exported_instances=[], format='XML'):
        '''
        format: {'XML' | 'JSON'}

            If I have already exported this instance I don't want to duplicate all details hence I just export it's URIInstance, 
            name and SimpleEntity URI. Then I need to add an attribute so that when importing it I will recognize that its details
            are somewhere else in the file
            <StructureNode URISimpleEntity="....." URIInstance="...." attribute="...." REFERENCE_IN_THIS_FILE=""
            the TAG "REFERENCE_IN_THIS_FILE" is used to mark the fact that the details of this SimpleEntity are somewhere else in the file
        '''
        format = format.upper()
        serialized = ""
        # if there is no etn I export just this object creating a shallow DataSetStructure 
        if etn is None:
            etn = self.shallow_dataset_structure().entry_point
        if etn.is_many:
            # the attribute correspond to a list of instances of the SimpleEntity 
            tag_name = etn.simple_entity.name
        else:
            tag_name = self.__class__.__name__ if etn.attribute == "" else etn.attribute
        # already exported, I just export a short reference with the URIInstance
        if self.URIInstance and self.URIInstance in exported_instances and etn.simple_entity.name_field:
            if format == 'XML':
                xml_name = " " + etn.simple_entity.name_field + "=\"" + getattr(self, etn.simple_entity.name_field) + "\""
                return '<' + tag_name + ' REFERENCE_IN_THIS_FILE=\"\"' + self.serialized_URI_SE(format) + xml_name + ' URIInstance="' + self.URIInstance + '"/>'  
            if format == 'JSON':
                xml_name = ' "' + etn.simple_entity.name_field + '" : "' + getattr(self, etn.simple_entity.name_field) + '"'
                if etn.is_many:
                    return ' { "REFERENCE_IN_THIS_FILE" : \"\", ' + self.serialized_URI_SE(format) + ", " + xml_name + ', "URIInstance": "' + self.URIInstance + '"} '
                else:
                    return '"' + tag_name + '" : { "REFERENCE_IN_THIS_FILE" : \"\", ' + self.serialized_URI_SE(format) + ", " + xml_name + ', "URIInstance": "' + self.URIInstance + '"}'  
        
        exported_instances.append(self.URIInstance) 
        if not etn.external_reference:
            try:
                outer_comma = ""
                for child_node in etn.child_nodes.all():
                    if child_node.is_many:
                        child_instances = eval("self." + child_node.attribute + ".all()")
                        if format == 'XML':
                            serialized += "<" + child_node.attribute + ">"
                        if format == 'JSON':
                            serialized += outer_comma + ' "' + child_node.attribute + '" : ['
                        innner_comma = ''
                        for child_instance in child_instances:
                            # let's prevent infinite loops if self relationships
                            if (child_instance.__class__.__name__ != self.__class__.__name__) or (self.pk != child_node.pk):
                                if format == 'JSON':
                                    serialized += innner_comma
                                serialized += child_instance.serialize(child_node, exported_instances=exported_instances, format=format)
                            innner_comma = ", "
                        if format == 'XML':
                            serialized += "</" + child_node.attribute + ">"
                        if format == 'JSON':
                            serialized += "]"
                    else:
                        child_instance = eval("self." + child_node.attribute)
                        if not child_instance is None:
                            serialized += child_instance.serialize(child_node, format=format, exported_instances=exported_instances)
                    outer_comma = ", "
            except Exception as es:
                print(str(es))
            if format == 'XML':
                return '<' + tag_name + self.serialized_URI_SE(format) + self.serialized_attributes(format) + '>' + serialized + '</' + tag_name + '>'
            if format == 'JSON':
                if etn.is_many:
                    return ' { ' + self.serialized_URI_SE(format) + ', ' + self.serialized_attributes(format) + outer_comma + serialized + ' }'
                else:
                    return '"' + tag_name + '" : { ' + self.serialized_URI_SE(format) + ', ' + self.serialized_attributes(format) + outer_comma + serialized + ' }'
            
        else:
            # etn.external_reference = True
            xml_name = ''
            json_name = ''
            if etn.simple_entity.name_field != "":
                if format == 'XML':
                    xml_name = " " + etn.simple_entity.name_field + "=\"" + getattr(self, etn.simple_entity.name_field) + "\""
                if format == 'JSON':
                    json_name = ', "' + etn.simple_entity.name_field + '": "' + getattr(self, etn.simple_entity.name_field) + '"'
            if format == 'XML':
                return '<' + tag_name + self.serialized_URI_SE() + 'URIInstance="' + self.URIInstance + '" ' + self._meta.pk.attname + '="' + str(self.pk) + '"' + xml_name + '/>'
            if format == 'JSON':
                if etn.is_many:
                    return '{ ' + self.serialized_URI_SE(format) + ', "URIInstance" : "' + self.URIInstance + '", "' + self._meta.pk.attname + '" : "' + str(self.pk) + '"' + json_name + ' }'
                else:
                    return '"' + tag_name + '" :  { ' + self.serialized_URI_SE(format) + ', "URIInstance" : "' + self.URIInstance + '", "' + self._meta.pk.attname + '" : "' + str(self.pk) + '"' + json_name + ' }'
            
    def new_version(self, etn, processed_instances, parent=None):
        '''
        invoked by DataSet.new_version that wraps it in a transaction
        it recursively invokes itself to create a new version of the full structure
        
        processed_instances is a dictionary where the key is the old URIInstance and 
        the data is the new one
        
        returns the newly created instance
        '''

        if etn.external_reference:
            # if it is an external reference I do not need to create a new instance
            return self

        if self.URIInstance and str(self.URIInstance) in processed_instances.keys():
            # already created, I return that one 
            return self.__class__.objects.get(URIInstance=processed_instances[str(self.URIInstance)])
        
        new_instance = self.__class__()
        if parent:
#           I have a parent; let's set it
            field_name = SerializableSimpleEntity.get_parent_field_name(parent, etn.attribute)
            if field_name:
                setattr(new_instance, field_name, parent)
                
        for en_child_node in etn.child_nodes.all():
            if en_child_node.attribute in self.foreign_key_attributes():
                # not is_many
                child_instance = eval("self." + en_child_node.attribute)
                new_child_instance = child_instance.new_version(en_child_node, processed_instances)
                setattr(new_instance, en_child_node.attribute, new_child_instance)  # the parameter "parent" shouldn't be necessary in this case as this is a ForeignKey
                
        # I have added all attributes corresponding to ForeignKey, I can save it so that I can use it as a parent for the other attributes
        new_instance.save()
                
        for en_child_node in etn.child_nodes.all():
            if en_child_node.is_many:
                child_instances = eval("self." + en_child_node.attribute + ".all()")
                for child_instance in child_instances:
                    # let's prevent infinite loops if self relationships
                    if (child_instance.__class__.__name__ == self.__class__.__name__) and (self.pk == en_child_node.pk):
                        eval("new_instance." + en_child_node.attribute + ".add(new_instance)")
                    else:
                        new_child_instance = child_instance.new_version(en_child_node, processed_instances, new_instance)
            else:
                # not is_many
                child_instance = eval("self." + en_child_node.attribute)
                new_child_instance = child_instance.new_version(en_child_node, processed_instances, self)
                setattr(new_instance, en_child_node.attribute, new_child_instance)
        
        for key in self._meta.fields:
            if key.__class__.__name__ != "ForeignKey" and self._meta.pk != key:
                setattr(new_instance, key.name, eval("self." + key.name))
        new_instance.URI_previous_version = new_instance.URIInstance
        new_instance.URIInstance = ""
        new_instance.save()
        # after saving
        processed_instances[str(self.URIInstance)] = new_instance.URIInstance
        return new_instance
        
    def materialize(self, etn, processed_instances, parent=None):
        '''
        invoked by DataSet.set_released that wraps it in a transaction
        it recursively invokes itself to copy the full structure to the materialized DB
        
        ASSERTION: URIInstance remains the same on the materialized database
        
        processed_instances is a list of processed URIInstance 
        
        TODO: before invoking this method a check is done to see whether it is already materialized; is it done always? 
        If so shall we move it inside this method?
        '''

        if etn.external_reference:
            try:
                return self.__class__.objects.using('ksm').get(URIInstance=self.URIInstance)
            except Exception as ex:
                new_ex = Exception("SerializableSimpleEntity.materialize: self.URIInstance: " + self.URIInstance + " searching it on ksm: " + ex.message)
                raise ex

        if self.URIInstance and str(self.URIInstance) in processed_instances:
            # already materialized it, I return that one 
            return self.__class__.objects.using('ksm').get(URIInstance=self.URIInstance)
        
        new_instance = self.__class__()
        if parent:
#           I have a parent; let's set it
            field_name = SerializableSimpleEntity.get_parent_field_name(parent, etn.attribute)
            if field_name:
                setattr(new_instance, field_name, parent)
          
        list_of_self_relationships_pointing_to_self = []      
        for en_child_node in etn.child_nodes.all():
            if en_child_node.attribute in self.foreign_key_attributes():
                # not is_many
                # if they are nullable I do nothing
                try:
                    child_instance = getattr(self, en_child_node.attribute)
                    
                    # e.g. DataSet.root is a self relationship often set to self; I am materializing self
                    # so I don't have it; I return self; I could probably do the same also in the other case
                    # because what actually counts for Django is the pk
                    if self == child_instance:
                        # In Django ORM it seems not possible to have not nullable self relationships pointing to self
                        # I make not nullable in the model (this becomes a general constraint!); 
                        # put them in a list and save them after saving new_instance
                        list_of_self_relationships_pointing_to_self.append(en_child_node.attribute)
                    else:
                        new_child_instance = child_instance.materialize(en_child_node, processed_instances)
                        setattr(new_instance, en_child_node.attribute, new_child_instance)  # the parameter "parent" shouldn't be necessary in this case as this is a ForeignKey
                except Exception as ex:
#                     print("SerializableSimpleEntity.materialize: " + self.__class__.__name__ + " " + str(self.pk) + " attribute \"" + en_child_node.attribute + "\" " + ex.message)
                    pass
        for key in self._meta.fields:
            if key.__class__.__name__ != "ForeignKey" and self._meta.pk != key:
                setattr(new_instance, key.name, eval("self." + key.name))
        
        # I have added all attributes corresponding to ForeignKey, I can save it so that I can use it as a parent for the other attributes
        new_instance.save(using='ksm')
        if len(list_of_self_relationships_pointing_to_self) > 0:
            for attribute in list_of_self_relationships_pointing_to_self:
                setattr(new_instance, attribute, new_instance)
            new_instance.save(using='ksm')
        
        for en_child_node in etn.child_nodes.all():
            if not (en_child_node.attribute in self.foreign_key_attributes()):
                if en_child_node.is_many:
                    child_instances = eval("self." + en_child_node.attribute + ".all()")
                    for child_instance in child_instances:
                        # let's prevent infinite loops if self relationships
                        if (child_instance.__class__.__name__ == self.__class__.__name__) and (self.pk == en_child_node.pk):
                            eval("new_instance." + en_child_node.attribute + ".add(new_instance)")
                        else:
                            new_child_instance = child_instance.materialize(en_child_node, processed_instances, new_instance)
                else:
                    # not is_many
                    child_instance = eval("self." + en_child_node.attribute)
                    new_child_instance = child_instance.materialize(en_child_node, processed_instances, self)
                    setattr(new_instance, en_child_node.attribute, new_child_instance)
        
        new_instance.save(using='ksm')
        # after saving
        processed_instances.append(new_instance.URIInstance)
        return new_instance
        
    def delete_children(self, etn, parent=None):
        '''
        invoked by DataSet.delete_entire_dataset that wraps it in a transaction
        it recursively invokes itself to delete children's children; self is in the 
        materialized database
        
        It is invoked only if DataSet.dataset_structure.multiple_releases = False
        Then I also have to remap foreign keys pointing to it in the materialized DB and
        in default DB
        '''

        # I delete the children; must do it before remapping foreignkeys otherwise some will escape deletion
        for en_child_node in etn.child_nodes.all():
            if not en_child_node.external_reference:
                if en_child_node.is_many:
                    child_instances = eval("self." + en_child_node.attribute + ".all()")
                    for child_instance in child_instances:
                        # let's prevent deleting self; self will be deleted by who has invoked this method 
                        if (child_instance.__class__.__name__ != self.__class__.__name__) or (self.pk != en_child_node.pk):
                            child_instance.delete_children(en_child_node, self)
                            child_instance.delete()
                else:
                    # not is_many
                    child_instance = eval("self." + en_child_node.attribute)
                    child_instance.delete_children(en_child_node, self)
                    child_instance.delete()
        
        try:
            # before deleting self I must remap foreignkeys pointing at it to the new instances
            # let's get the instance it should point to
            '''
            There could be more than one; imagine the case of an Italian Province split into two of them (Region Sardinia
            had four provinces and then they become 4) then there will be two new instances with the same URI_previous_version.
            TODO: we should also take into account the case when a new_materialized_instance can have more than URI_previous_version; this
            situation requires redesign of the model and db
            '''
            new_materialized_instances = self.__class__.objects.using('ksm').filter(URI_previous_version=self.URIInstance)
            new_instances = self.__class__.objects.filter(URI_previous_version=self.URIInstance)
            self_on_default_db = self.__class__.objects.filter(URIInstance=self.URIInstance)
            
            assert (len(new_materialized_instances) == len(new_instances)), 'SerializableSimpleEntity.delete_children self.URIInstance="' + self.URIInstance + '": "(len(new_materialized_instances ' + str(new_materialized_instances) + ') != len(new_instances' + str(new_instances) + '))"'
            if len(new_materialized_instances) == 1:
                new_materialized_instance = new_materialized_instances[0]
                new_instance = new_instances[0]
                # I NEED TO LIST TODO:ALL THE RELATIONSHIPS POINTING AT THIS MODEL
                for rel_key in self._meta.fields_map.keys():
                    rel = self._meta.fields_map[rel_key]
                    if rel.__class__.__name__ == 'ManyToOneRel':
                        related_name = rel.related_name
                        if related_name is None:
                            related_name = rel_key + "_set"
                        related_materialized_instances_manager = getattr(self, related_name)
                        related_instances_manager = getattr(self_on_default_db, related_name)
                        # running      related_materialized_instances_manager.update(rel.field.name=new_materialized_instance)
                        # raises       SyntaxError: keyword can't be an expression
                        # update relationship on the materialized DB
                        eval('related_materialized_instances_manager.update(' + rel.field.name + '=new_materialized_instance)')
                        # update relationship on default DB
                        eval('related_instances_manager.update(' + rel.field.name + '=new_instance)')
            else:
                raise Exception('NOT IMPLEMENTED in SerializableSimpleEntity.delete_children: mapping between different versions: URIInstance "' + self.URIInstance + '" has ' + str(len(new_instances)) + ' materialized records that have this as URI_previous_version.') 
        except Exception as e:
            print(e.message)
            
    @staticmethod
    def simple_entity_from_xml_tag(xml_child_node):
        URIInstance = xml_child_node.attributes["URISimpleEntity"].firstChild.data
        try:
            se = SimpleEntity.objects.get(URIInstance=URIInstance)
        except:
            '''
            I go get it from the appropriate KS
            TODO: David
            See API definition here: http://redmine.davide.galletti.name/issues/33
            When I get a SimpleEntity I must generate its model in an appropriate module; the module
            name must be generated so that it is unique based on the SimpleEntity's BASE URI and on the module 
            name; 
            SimpleEntity URI 1: "http://finanze.it/KS/fattura"
            SimpleEntity URI 2: "http://finanze.it/KS/sanzione"
            
            TODO: When importing an DataSet from another KS, its root will point to either self or to an DataSet
            that is on the other KS; in the latter case I search for this root DataSet using the field 
            SerializableSimpleEntity.URI_imported_instance; if I find it I set root to point to it otherwise
            I set it to self.
            '''
            # estrarre l'url del KS
            ks_url = ""
            # encode di URIInstance
            URIInstance_base64 = ""
            # wget ks_url + "/ks/api/simple_entity_definition/" + URIInstance_base64
            raise Exception("NOT IMPLEMENTED in simple_entity_from_xml_tag: get SimpleEntity from appropriate KS.")
        return se

    def from_xml(self, xmldoc, structure_node, insert=True, parent=None):
        '''
        from_xml gets from xmldoc the attributes of self and saves it; it searches for child nodes according
        to what the structure_node says, creates instances of child objects and call itself recursively
        Every tag corresponds to a SimpleEntity, hence it
            contains a tag URISimpleEntity which points to the KS managing the SimpleEntity definition
        
        Each SerializableSimpleEntity has URIInstance and URI_imported_instance attributes. 
        
        external_reference
            the first SimpleEntity in the XML cannot be marked as an external_reference in the structure_node
            from_xml doesn't get called recursively for external_references which are sought in the database
            or fetched from remote KS, so I assert self it is not an external reference
        
        '''
        logger = utils.poor_mans_logger()
        field_name = ""
        if parent:
#           I have a parent; let's set it
            field_name = SerializableSimpleEntity.get_parent_field_name(parent, structure_node.attribute)
            if field_name:
                setattr(self, field_name, parent)
        '''
        Some TAGS have no data (attribute REFERENCE_IN_THIS_FILE is present) because the instance they describe
        is present more than once in the XML file and the export doesn't replicate data; hence either
           I have it already in the database so I can load it
        or
           I have to save this instance but I will find its attribute later in the imported file
        '''
        try:
            xmldoc.attributes["REFERENCE_IN_THIS_FILE"]
            # if the TAG is not there an exception will be raised and the method will continue and expect to find all data
            module_name = structure_node.simple_entity.module
            actual_class = utils.load_class(module_name + ".models", structure_node.simple_entity.name) 
            try:
                instance = actual_class.retrieve(xmldoc.attributes["URIInstance"].firstChild.data)
                # It's in the database; I just need to set its parent; data is either already there or it will be updated later on
                if parent:
                    field_name = SerializableSimpleEntity.get_parent_field_name(parent, structure_node.attribute)
                    if field_name:
                        setattr(instance, field_name, parent)
                    instance.save()
            except:
                # I haven't found it in the database; I need to do something only if I have to set the parent
                if parent: 
                    try:
                        setattr(self, "URIInstance", xmldoc.attributes["URIInstance"].firstChild.data)
                        self.SetNotNullFields()
                        self.save()
                    except:
                        logger.error("Error in REFERENCE_IN_THIS_FILE TAG setting attribute URIInstance for instance of class " + self.__class__.__name__)
            # let's exit, nothing else to do, it's a REFERENCE_IN_THIS_FILE
            return
             
        except:
            # nothing to do, there is no REFERENCE_IN_THIS_FILE attribute
            pass
        for key in self._meta.fields:
            '''
              let's setattr the other attributes
              that are not ForeignKey as those are treated separately
              and is not the field_name pointing at the parent as it has been already set
              TODO: if insert: I shouldn't set the pk; I set it to None later but it should be done here
            '''
            if key.__class__.__name__ != "ForeignKey" and (not parent or key.name != field_name):
                try:
                    if key.__class__.__name__ == "BooleanField":
                        setattr(self, key.name, xmldoc.attributes[key.name].firstChild.data.lower() == "true") 
                    elif key.__class__.__name__ == "IntegerField":
                        setattr(self, key.name, int(xmldoc.attributes[key.name].firstChild.data))
                    else:
                        setattr(self, key.name, xmldoc.attributes[key.name].firstChild.data)
                except:
                    logger.error("Error extracting from xml \"" + key.name + "\" for object of class \"" + self.__class__.__name__ + "\" with PK " + str(self.pk))

        # I set the URIInstance to "" so that one is generated automatically; URI_imported_instance is the field
        # that allows me to track provenance
        self.URIInstance = ""
        try:
            # URI_imported_instance stores the URIInstance from the XML
            self.URI_imported_instance = xmldoc.attributes["URIInstance"].firstChild.data
        except:
            # there's no URIInstance in the XML; it doesn't make sense but it will be created from scratch here
            pass
        # I must set foreign_key child nodes BEFORE SAVING self otherwise I get an error for ForeignKeys not being set
        for en_child_node in structure_node.child_nodes.all():
            if en_child_node.attribute == 'root':
                pass
            elif en_child_node.attribute in self.foreign_key_attributes():
                try:
                    # ASSERT: in the XML there is exactly at most one child tag
                    child_tag = xmldoc.getElementsByTagName(en_child_node.attribute)
                    if len(child_tag) == 1:
                        xml_child_node = xmldoc.getElementsByTagName(en_child_node.attribute)[0] 
                        # I search for the corresponding SimpleEntity
                         
                        se = SerializableSimpleEntity.simple_entity_from_xml_tag(xml_child_node)
                        # TODO: I'd like the module name to be function of the organization and namespace
                        assert (en_child_node.simple_entity.name == se.name), "en_child_node.simple_entity.name - se.name: " + en_child_node.simple_entity.name + ' - ' + se.name
                        module_name = en_child_node.simple_entity.module
                        actual_class = utils.load_class(module_name + ".models", en_child_node.simple_entity.name)
                        if en_child_node.external_reference:
                            '''
                            If it is an external reference I must search for it in the database first;  
                            if it is not there I fetch it using it's URI and then create it in the database
                            '''
                            # it can be a self relation; if so instance is self
                            if self.URIInstance == xml_child_node.attributes["URIInstance"].firstChild.data:
                                instance = self 
                            else:
                                try:
                                    # let's search it in the database
                                    instance = actual_class.retrieve(xml_child_node.attributes["URIInstance"].firstChild.data)
                                except ObjectDoesNotExist:
                                    # TODO: if it is not there I fetch it using it's URI and then create it in the database
                                    pass
                                except Exception as ex:
                                    logger.error("\"" + module_name + ".models " + se.name + "\" has no instance with URIInstance \"" + xml_child_node.attributes["URIInstance"].firstChild.data + " " + ex.message)
                                    raise Exception("\"" + module_name + ".models " + se.name + "\" has no instance with URIInstance \"" + xml_child_node.attributes["URIInstance"].firstChild.data + " " + ex.message)
                        else:
                            if insert:
                                # the user asked to "always create", let's create the instance
                                instance = actual_class()
                            else:
                                try:
                                    instance = actual_class.retrieve(xml_child_node.attributes["URIInstance"].firstChild.data)
                                except:
                                    # didn't find it; I create the instance anyway
                                    instance = actual_class()
                            # from_xml takes care of saving instance with a self.save() at the end
                            instance.from_xml(xml_child_node, en_child_node, insert)  # the fourth parameter, "parent" shouldn't be necessary in this case as this is a ForeignKey
                        setattr(self, en_child_node.attribute, instance)
                except Exception as ex:
                    logger.error("from_xml: " + ex.message)
                    raise Exception("from_xml: " + ex.message)
                 
        # I have added all attributes corresponding to ForeignKey, I can save it so that I can use it as a parent for the other attributes
        if insert:
            # TODO: UGLY PATCH: see #143
            if self.__class__.__name__ == 'DataSet':
                self.root = None
            # but first I have reset the pk as it could exist in this database
            self.pk = None
        self.save()
        if insert:
            # TODO: UGLY PATCH: see #143
            if self.__class__.__name__ == 'DataSet':
                '''
                if the root (version) has been imported here then I set it as a root, otherwise self
                '''
                self.root = self
                try:
                    root_tag = xmldoc.getElementsByTagName('root')
                    if len(root_tag) == 1:
                        root_URIInstance = xmldoc.getElementsByTagName('root')[0].attributes["URIInstance"].firstChild.data
                        instance = DataSet.retrieve(root_URIInstance)
                        self.root = instance
                except:
                    pass
                self.save()
        # from_xml can be invoked on an instance retrieved from the database (where URIInstance is set)
        # or created on the fly (and URIInstance is not set); in the latter case, only now I can generate URIInstance
        # as I have just saved it and I have a local ID
        
        for en_child_node in structure_node.child_nodes.all():
            # I have already processed foreign keys, I skip them now
            if (not en_child_node.attribute in self.foreign_key_attributes()):
                # ASSERT: in the XML there is exactly one child tag
                xml_attribute_node = xmldoc.getElementsByTagName(en_child_node.attribute)[0]
                if en_child_node.is_many:
                    for xml_child_node in xml_attribute_node.childNodes:
                        se = SerializableSimpleEntity.simple_entity_from_xml_tag(xml_child_node)
                        module_name = en_child_node.simple_entity.module
                        assert (en_child_node.simple_entity.name == se.name), "en_child_node.name - se.name: " + en_child_node.simple_entity.name + ' - ' + se.name
                        actual_class = utils.load_class(module_name + ".models", en_child_node.simple_entity.name)
                        if en_child_node.external_reference:
                            instance = actual_class.retrieve(xml_child_node.attributes["URIInstance"].firstChild.data)
                            # TODO: il test succesivo forse si fa meglio guardando il concrete_model - capire questo test e mettere un commento
                            if en_child_node.attribute in self._meta.fields:
                                setattr(instance, en_child_node.attribute, self)
                                instance.save()
                            else:  
                                setattr(self, en_child_node.attribute, instance)
                                self.save()
                        else:
                            if insert:
                                instance = actual_class()
                            else:
                                try:
                                    instance = actual_class.retrieve(xml_child_node.attributes["URIInstance"].firstChild.data)
                                except:
                                    instance = actual_class()
                            # is_many = True, I need to add this instance to self
                            instance.from_xml(xml_child_node, en_child_node, insert, self)
                            related_parent = getattr(self._meta.concrete_model, en_child_node.attribute)
                            related_list = getattr(self, en_child_node.attribute)
                            # if it is not there yet ...
                            if long(instance.id) not in [long(i.id) for i in related_list.all()]:
                                # I add it
                                related_list.add(instance)
                                self.save()
                else:
                    # is_many == False
                    xml_child_node = xml_attribute_node
                    se = SerializableSimpleEntity.simple_entity_from_xml_tag(xml_child_node)
                    module_name = en_child_node.simple_entity.module
                    assert (en_child_node.simple_entity.name == se.name), "en_child_node.name - se.name: " + en_child_node.simple_entity.name + ' - ' + se.name
                    actual_class = utils.load_class(module_name + ".models", en_child_node.simple_entity.name)
                    if en_child_node.external_reference:
                        instance = actual_class.retrieve(xml_child_node.attributes["URIInstance"].firstChild.data)
                        # TODO: il test succesivo forse si fa meglio guardando il concrete_model - capire questo test e mettere un commento
                        if en_child_node.attribute in self._meta.fields:
                            setattr(instance, en_child_node.attribute, self)
                            instance.save()
                        else:  
                            setattr(self, en_child_node.attribute, instance)
                            self.save()
                    else:
                        if insert:
                            instance = actual_class()
                        else:
                            try:
                                instance = actual_class.retrieve(xml_child_node.attributes["URIInstance"].firstChild.data)
                            except:
                                instance = actual_class()
                        instance.from_xml(xml_child_node, en_child_node, insert, self)
        
    @classmethod
    def retrieve(cls, URIInstance):
        '''
        It returns an instance of a SerializableSimpleEntity stored in this KS
        It searches first on the URIInstance field (e.g. is it already an instance of this KS? ) 
        It searches then on the URI_imported_instance field (e.g. has is been imported in this KS from the same source? )
        It fetches the instance from the source as it is not in this KS yet 
        '''
        actual_instance = None
        try:
            actual_instance = cls.objects.get(URIInstance=URIInstance)
        except Exception as ex:
            try:
                actual_instance = cls.objects.get(URI_imported_instance=URIInstance)
            except Exception as ex:
                raise ex
        return actual_instance

    @staticmethod
    def get_parent_field_name(parent, attribute):
        '''
        TODO: describe *ObjectsDescriptor or link to docs
              make sure it is complete (e.g. we are not missing any other *ObjectsDescriptor)
        '''
        field_name = ""
        related_parent = getattr(parent._meta.concrete_model, attribute)
        if related_parent.__class__.__name__ == "ForeignRelatedObjectsDescriptor":
            field_name = related_parent.related.field.name
        if related_parent.__class__.__name__ == "ReverseSingleRelatedObjectDescriptor":
            field_name = related_parent.field.name
        return field_name

    @staticmethod
    def compare(first, second):
        return first.serialized_attributes() == second.serialized_attributes()

    @staticmethod
    def intersect_list(first, second):
        first_URIInstances = list(i.URIInstance for i in first)
        return filter(lambda x: x.URIInstance in first_URIInstances, second)

    class Meta:
        abstract = True

class DBConnection(models.Model):
    connection_string = models.CharField(max_length=255L)
    name = models.CharField(max_length=100L, null=True, blank=True)
    description = models.CharField(max_length=2000L, null=True, blank=True)

class Workflow(SerializableSimpleEntity):
    '''
    Is a list of WorkflowMethods; the work-flow is somehow abstract, its methods do not specify details of 
    the operation but just the statuses
    '''
    name = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    dataset_structure = models.ForeignKey('DataSetStructure', null=True, blank=True)
#     ASSERT: I metodi di un wf devono avere impatto solo su SimpleEntity contenute nel DataSetStructure

class WorkflowMethod(SerializableSimpleEntity):
    '''
    If there are no initial_statuses then this is a method which creates the entity
    '''
    initial_statuses = models.ManyToManyField("WorkflowStatus", blank=True, related_name="+")
    final_status = models.ForeignKey("WorkflowStatus", related_name="+")
    workflow = models.ForeignKey(Workflow)

class WorkflowStatus(SerializableSimpleEntity):
    '''
    '''
    name = models.CharField(max_length=100L)
    workflow = models.ForeignKey(Workflow, null=True, blank=True)
    description = models.CharField(max_length=2000L, blank=True)

class WorkflowDataSet(models.Model):
    '''
    WorkflowDataSet
    '''
    workflow = models.ForeignKey(Workflow)
    current_status = models.ForeignKey(WorkflowStatus)
    class Meta:
        abstract = True

class WorkflowTransition(SerializableSimpleEntity):
    dataset = models.ForeignKey("DataSet")
    workflow_method = models.ForeignKey('WorkflowMethod')
    notes = models.TextField()
    # TODO: non voglio null=True ma non so come gestire la migration nella quale mi chiede un default value 
    user = models.ForeignKey(KUser, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_from = models.ForeignKey(WorkflowStatus, related_name="+")

class Organization(SerializableSimpleEntity):
    name = models.CharField(max_length=500L, blank=True)
    description = models.CharField(max_length=2000L, blank=True)
    website = models.CharField(max_length=500L, blank=True)

class KnowledgeServer(SerializableSimpleEntity):
    name = models.CharField(max_length=500L, blank=True)
    description = models.CharField(max_length=2000L, blank=True)
    # ASSERT: only one KnowledgeServer in each KS has this_ks = True; I use it to know in which KS I am
    this_ks = models.BooleanField(default=False)
    # urlparse terminology https://docs.python.org/2/library/urlparse.html
#     scheme e.g. { "http" | "https" }
    scheme = models.CharField(max_length=50L)
#     netloc e.g. "ks.thekoa.org"
    netloc = models.CharField(max_length=200L)
#     html_home text that gets displayed at the home page
    html_home = models.CharField(max_length=4000L, default="")
#     html_disclaimer text that gets displayed at the disclaimer page
    html_disclaimer = models.CharField(max_length=4000L, default="")
    
    organization = models.ForeignKey(Organization)
    def uri(self, encode_base64=False):
        # "http://rootks.thekoa.org/"
        uri = self.scheme + "://" + self.netloc
        if encode_base64:
            uri = base64.encodestring(uri).replace('\n', '')
        return uri
    
    def run_cron(self):
        '''
        This method processes notifications received, generate notifications to be sent
        if events have occurred, ...
        '''
        response = self.process_events()
        response += self.send_notifications()
        response += self.process_received_notifications()
        return response
        
    def process_events(self):
        '''
        Events are transformed in notifications to be sent
        "New version" is the only event so far
        
        Subscriptions to a released dataset generates a notification too, only once though
        '''
        message = "Processing events that could generate notifications<br>"
        # subscriptions
        subs_first_time = SubscriptionToThis.objects.filter(first_notification_prepared=False)
        message += "Found " + str(len(subs_first_time)) + " subscriptions to data in this OKS<br>"
        for sub in subs_first_time:
            try:
                with transaction.atomic():
                    # I get the DataSet from the subscription (it is the root)
                    root_ei = DataSet.objects.get(URIInstance=sub.root_URIInstance)
                    event = Event()
                    event.dataset = root_ei.get_latest(True)
                    event.type = "First notification"
                    event.processed = True
                    event.save()
                    n = Notification()
                    n.event = event
                    n.remote_url = sub.remote_url
                    n.save()
                    sub.first_notification_prepared = True
                    sub.save()
            except Exception as e:
                message += "process_events, subscriptions error: " + e.message
                print (str(e))
            
        # events
        events = Event.objects.filter(processed=False, type="New version")
        message += "Found " + str(len(events)) + " events<br>"
        for event in events:
            subs = SubscriptionToThis.objects.filter(root_URIInstance=event.dataset.root.URIInstance)
            try:
                with transaction.atomic():
                    for sub in subs:
                        # I do not want to send two notifications if "First notification" and "New version" happen at the same time
                        if not sub in subs_first_time:
                            n = Notification()
                            n.event = event
                            n.remote_url = sub.remote_url
                            n.save()
                    event.processed = True
                    event.save()
            except Exception as e:
                message += "process_events, events error: " + e.message
                print (str(e))
        return message + "<br>"
    
    def send_notifications(self):
        '''
        '''
        message = "Sending notifications<br>"
        try:
            this_ks = KnowledgeServer.this_knowledge_server()
            notifications = Notification.objects.filter(sent=False)
            message += "Found " + str(len(notifications)) + " notifications<br>"
            for notification in notifications:
                message += "send_notifications, found a notification for URIInstance " + notification.event.dataset.URIInstance + "<br>"
                message += "about to notify " + notification.remote_url + "<br>"
                m_es = DataSetStructure.objects.using('ksm').get(name=DataSetStructure.dataset_structure_name)
                es = DataSetStructure.objects.using('default').get(URIInstance=m_es.URIInstance)
                this_es = DataSetStructure.objects.get(URIInstance=notification.event.dataset.dataset_structure.URIInstance)
                ei_of_this_es = DataSet.objects.get(entry_point_instance_id=this_es.id, dataset_structure=es)
                values = { 'root_URIInstance' : notification.event.dataset.root.URIInstance,
                           'URL_dataset' : this_ks.uri() + reverse('api_dataset', args=(base64.encodestring(notification.event.dataset.URIInstance).replace('\n', ''), "XML",)),
                           'URL_structure' : this_ks.uri() + reverse('api_dataset', args=(base64.encodestring(ei_of_this_es.URIInstance).replace('\n', ''), "XML",)),
                           'type' : notification.event.type,
                           'timestamp' : notification.event.timestamp, }
                data = urllib.urlencode(values)
                req = urllib2.Request(notification.remote_url, data)
                response = urllib2.urlopen(req)
                ar = ApiReponse()
                ar.parse(response.read())
                if ar.status == "success":
                    notification.sent = True
                    notification.save()
                else:
                    message += "send_notifications " + notification.remote_url + " responded: " + ar.message + "<br>"
        except Exception as e:
            message += "send_notifications error: " + e.message
        return message + "<br>"
    
    def process_received_notifications(self):
        '''
        '''
        message = "Processing received notifications<br>"
        notifications = NotificationReceived.objects.filter(processed=False)
        message += "Found " + str(len(notifications)) + " notifications<br>"
        for notification in notifications:
            try:
                with transaction.atomic():
                    # We assume we have already all SimpleEntity
                    # Let's retrieve the structure
                    response = urllib2.urlopen(notification.URL_structure)
                    structure_xml_stream = response.read()
                    ei_structure = DataSet()
                    ei_structure = ei_structure.from_xml_with_actual_instance(structure_xml_stream)
                    ei_structure.dataset_structure = DataSetStructure.objects.get(name=DataSetStructure.dataset_structure_name)
                    ei_structure.materialize_dataset()
                    # the dataset is retrieved with api #36 api_dataset that serializes
                    # the DataSet and also the complete actual instance 
                    # from_xml_with_actual_instance will create the DataSet and the actual instance
                    response = urllib2.urlopen(notification.URL_dataset)
                    dataset_xml_stream = response.read()
                    ei = DataSet()
                    ei = ei.from_xml_with_actual_instance(dataset_xml_stream)
                    ei.dataset_structure = ei_structure.get_instance()
                    ei.materialize_dataset()
                    notification.processed = True
                    notification.save()
            except Exception as ex:
                message += "process_received_notifications error: " + ex.message
        return message + "<br>"
        
    @staticmethod
    def this_knowledge_server(db_alias='ksm'):
        '''
        *** method that works BY DEFAULT on the materialized database ***
        *** the reason being that only there "get(this_ks = True)" is ***
        *** guaranteed to return exactly one record                   ***
        when working on the default database we must first fetch it on the
        materialized; then, using the URIInstance we search it on the default
        because the URIInstance will be unique there
        '''
        materialized_ks = KnowledgeServer.objects.using('ksm').get(this_ks=True)
        if db_alias == 'default':
            return KnowledgeServer.objects.using('default').get(URIInstance=materialized_ks.URIInstance)
        else:
            return materialized_ks
    
class SimpleEntity(SerializableSimpleEntity):
    '''
    A SimpleEntity roughly corresponds to a table in a database or a class if we have an ORM
    '''
    # this name corresponds to the class name
    name = models.CharField(max_length=100L)
    # for Django it corresponds to the module which contains the class 
    module = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, default="")
    table_name = models.CharField(max_length=255L, db_column='tableName', default="")
    id_field = models.CharField(max_length=255L, db_column='idField', default="id")
    name_field = models.CharField(max_length=255L, db_column='nameField', default="name")
    description_field = models.CharField(max_length=255L, db_column='descriptionField', default="description")
    connection = models.ForeignKey(DBConnection, null=True, blank=True)
    '''
    dataset_structure attribute is not in NORMAL FORM! When not null it tells in which DataSetStructure is this 
    SimpleEntity; a SimpleEntity must be in only one DataSetStructure for version/state purposes! It can be in
    other DataSetStructure that are used as views.
    '''
    dataset_structure = models.ForeignKey("DataSetStructure", null=True, blank=True)
    
    def dataset_types(self, is_shallow=False, is_a_view=False, external_reference=False):
        '''
        returns the list of the types in which self is present as a node's SimpleEntity
        if only_versioned: skips views and shallow ones
        '''
        types = []
        nodes = StructureNode.objects.using('ksm').filter(simple_entity=self, external_reference=external_reference)
        try:
            for node in nodes:
                entry_node = node
                visited_nodes_ids = []
                visited_nodes_ids.append(entry_node.id)
                while len(entry_node.parent.all()) > 0:
                    for parent in entry_node.parent.all():
                        if parent.id not in visited_nodes_ids:
                            entry_node = parent
                            visited_nodes_ids.append(entry_node.id)
                            break
                dataset_type = entry_node.dataset_type.all()[0]
                if (not dataset_type in types) and dataset_type.is_shallow == is_shallow and dataset_type.is_a_view == is_a_view:
                    types.append(dataset_type)
        except Exception as ex:
            print ("dataset_types type(self): " + str(type(self)) + " self.id " + str(self.id) + ex.message)
            print ("visited_nodes_ids : " + str(visited_nodes_ids))
        return types

class AttributeType(SerializableSimpleEntity):
    name = models.CharField(max_length=255L, blank=True)
    widgets = models.ManyToManyField('application.Widget', blank=True)

class Attribute(SerializableSimpleEntity):
    name = models.CharField(max_length=255L, blank=True)
    simple_entity = models.ForeignKey('SimpleEntity', null=True, blank=True)
    type = models.ForeignKey('AttributeType')
    def __str__(self):
        return self.simple_entity.name + "." + self.name

class StructureNode(SerializableSimpleEntity):
    simple_entity = models.ForeignKey('SimpleEntity')
    # attribute is blank for the entry point
    attribute = models.CharField(max_length=255L, blank=True)
    # "parent" assert: there is only one parent so we should change to 
    # TODO: parent = models.ForeignKey('StructureNode', null=True, blank=True)
    child_nodes = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="parent")
    # if not external_reference all attributes are exported, otherwise only the id
    external_reference = models.BooleanField(default=False, db_column='externalReference')
    # is_many is true if the attribute correspond to a list of instances of the SimpleEntity
    is_many = models.BooleanField(default=False, db_column='isMany')

    def navigate(self, instance, instance_method_name, node_method_name, status, children_before):
        # I invoke the method on the instance and recursively on each children
        if instance_method_name:
            instance_method = getattr(instance, instance_method_name)
        if node_method_name:
            node_method = getattr(self, node_method_name)
        if not children_before and instance_method_name:
            instance_method(instance, status)
        if not children_before and node_method_name:
            node_method(instance, status)
        # loop on children

        for child_node in self.child_nodes.all():
            if child_node.is_many:
                child_instances = eval("instance." + child_node.attribute + ".all()")
                for child_instance in child_instances:
                    # let's prevent infinite loops if self relationships
                    if (child_instance.__class__.__name__ != instance.__class__.__name__) or (instance.pk != child_node.pk):
                        child_node.navigate(child_instance, instance_method_name, node_method_name, status, children_before)
            else:
                child_instance = eval("instance." + child_node.attribute)
                if not child_instance is None:
                    child_node.navigate(child_instance, instance_method_name, node_method_name, status, children_before)
            
        if children_before and instance_method_name:
            instance_method(instance, status)
        if children_before and node_method_name:
            node_method(instance, status)
        
    def navigate_helper_list_by_type(self, instance, status):
        # se statusoutput is None creo un dictionary
        # le cui chiavi sono i tipi di simpleentity e il cui valore è una lista senza ripetizioni delle istanze
        if not 'output' in status.keys():
            status['output'] = {}
        if not self.simple_entity in status['output'].keys():
            status['output'][self.simple_entity] = []
        if not instance in status['output'][self.simple_entity]:
            status['output'][self.simple_entity].append(instance)
        
class DataSetStructure(SerializableSimpleEntity):
    dataset_structure_name = "Dataset structure"
    simple_entity_dataset_structure_name = "Entity"
    workflow_dataset_structure_name = "Workflow"
    organization_dataset_structure_name = "Organization and Open Knowledge Servers"
    '''
    Main idea behind the model: an Entity is not represented with a single class or a single 
    table in a database but it is usually represented using a collection of them: more than 
    one class and more than one table in the database. An Issue in a tracking system is an 
    DataSetStructure; it has a list of notes that can be appended to it, it has a user who has created
    it, and many other attributes. The user does not belong just to this DataSetStructure, hence it
    is a reference; the notes do belong to the issue. The idea is to map the set of tables
    in a (relational) database into entities so that our operations can handle this more
    generic DataSetStructure that we are defining, composed with more than one SimpleEntity (in 
    more direct correspondence with a database table, SimpleEntity in our model). A simple
    entity can be in more than one DataSetStructure; because, for instance, we might like to render/...
    .../export/... a subset of the simple entities of a complex entity.
    When we get to DataSet (which inherits from VersionableDataSet and 
    WorkflowDataSet) we must add a constraint because we want a unique way
    to know the version and the status of a simple instance: take the set of entities
    in the DataSetStructure attribute of all instances of DataSet. In the graph of each
    DataSetStructure, consider only the simple entities that are not references; the constraint
    is that each SimpleEntity must not be in the graph of more than one DataSetStructure; otherwise
    it would be impossible to determine its version and status. In other words the entities
    used by DataSet must partition the E/R diagram of our database in graphs without
    any intersection. 
     
    A DataSetStructure is a graph that defines a set of simple entities on which we can perform a task; 
    it has an entry point which is a Node e.g. an DataSetStructure; from an instance of an DataSetStructure we can use
    the "attribute" attribute from the corresponding StructureNode to get the instances of
    the entities related to each of the child_nodes. An DataSetStructure could, for example, tell
    us what to export to xml/json, ???????????????? what to consider as a "VersionableMultiEntity" (e.g. an
    instance of VersionableDataSet + an DataSetStructure where the entry_point points to that instance)
    The name should describe its use ?????????????????
    
    Types of DataSetStructure
    versionable  : they are the default, used to define the structure of an DataSet
                   CONSTRAINT: if a SimpleEntity is in one of them it cannot be in another one of them
    shallow      : created automatically to export a SimpleEntity
                   CONSTRAINT: only one shallow per SimpleEntity 
    view         : used for example to export a structure different from one of the above; it has no version information
    
    CHECK: Only versionable and view are listed on the OKS and other systems can subscribe to.
    '''
    name = models.CharField(max_length=200L)
    description = models.CharField(max_length=2000L)
    '''
    an DataSetStructure is shallow when it is automatically created to export a SimpleEntity; 
    is_shallow = True means that all foreignKeys and related attributes are external references
    '''
    is_shallow = models.BooleanField(default=False)
    '''
    an DataSetStructure is a view if it is not used to determine the structure of an DataSet
    hence it is used for example to export some data
    '''
    is_a_view = models.BooleanField(default=False)
    '''
    the entry point of the structure; the class StructureNode has then child_nodes of the same class 
    hence it defines the structure
    assert: the entry_point is the entr_point for only one structure so we should change to 
    TODO: entry_point = models.OneToOneField('StructureNode', related_name="dataset_type")
    '''
    entry_point = models.ForeignKey('StructureNode', related_name='dataset_type')
    '''
    when multiple_releases is true more than one instance get materialized
    otherwise just one; it defaults to False just not to make it nullable;
    a default is indicated as shallow structures are created without specifying it
    makes no sense when is_a_view
    '''
    multiple_releases = models.BooleanField(default=False)
    
    '''
    TODO: the namespace is defined in the organization owner of this DataSetStructure
    within that organization (or maybe within the KS in that Organization)
    names of SimpleEntity are unique. When importing a SimpleEntity from
    an external KS we need to create a namespace (and a corresponding module
    where the class of the model must live) with a unique name. It can
    be done combining the netloc of the URI of the KS with the namespace;
    so when I import a WorkFlow from the namespace "entity" of rootks.thekoa.org 
    in my local KS it will live in the namespace/module:
        something like: rootks.thekoa.org_entity
    Within that namespace the KS it originated from ensures the SimpleEntity name
    is unique; locally in my KS I make sure there is no other namespace of that form
    (maybe not allowing "_"?)
    '''
    namespace = models.CharField(max_length=500L, blank=True)
    
    def navigate(self, dataset, instance_method_name, node_method_name, children_before = True):
        '''
        Many methods do things on each node navigating in the structure
        This is a generic method that takes a method as a parameter
        and executes it on the actual instance of each node; the signature of such method must be:
            def generic_structure_node_method(self, instance, status)
        each method can add whatever it wants to the status and set its output to status.output
        the instance_method_name must be a method of SerializableSimpleEntity so that it is implemented
        by any instance of any node.
        If children_before the method is invoked on the children first
        '''
        status = {}
        if self.is_a_view:
            # I have to do it on all instances that match the dataset criteria
            for instance in dataset.get_instances():
                self.entry_point.navigate(instance, instance_method_name, node_method_name, status, children_before)
        else:
            instance = dataset.get_instance()
            self.entry_point.navigate(instance, instance_method_name, node_method_name, status, children_before)
        return status['output']
    

class DataSet(SerializableSimpleEntity):
    '''
    A data set / chunk of knowledge; its data structure is described by self.dataset_structure
    The only Versionable object so far
    Serializable like many others 
    It has an owner KS which can be inferred by the URIInstance but it is explicitly linked 

    An DataSet is Versionable so there are many datasets that are basically different
    versions of the same thing; they share the same "root" attribute
    
    It will inherit from WorkflowDataSet when we will implement workflow features
    
    Relevant methods:
        new version: create new instances starting from entry point, following the nodes but those with external_reference=True
        set_released: it sets version_released True and it sets it to False for all the other instances of the same set
    '''
    owner_knowledge_server = models.ForeignKey(KnowledgeServer)

    # if the structure is intended to be a view there won't be any version information
    # assert dataset_structure.is_a_view ===> root, version, ... == None
    dataset_structure = models.ForeignKey(DataSetStructure)

    # if it is a view a description might be useful
    description = models.CharField(max_length=2000L, default="")
    
    # we have the ID of the instance because we do not know its class so we can't have a ForeignKey to an unknown class
    entry_point_instance_id = models.IntegerField(null=True, blank=True)

    # An alternative to the entry_point_instance_id is to have a filter to apply to the all the objects of type entry_point.instance
    # assert 
    #     filter_text != None ===> entry_point_instance_id == None
    #     entry_point_instance_id != None ===> filter_text == None
    # if entry_point_instance_id == None filter_text can be "" meaning that you have to take all of the entries without filtering them
    filter_text = models.CharField(max_length=200L, null=True, blank=True)

    # when the entry_point_instance_id is None (hence the structure is a view) I still might want to refer to a version for the data
    # that will be in my view; there might be data belonging to different versions matching the criteria in the filter text; to prevent
    # this I specify an DataSet (that has its own version) so that I will put in the view only those belonging to that version
    filter_dataset = models.ForeignKey('self', null=True, blank=True)
    # NOT USED YET: TODO: it should be used in get_instances
    # if filter_dataset is None then the view will filter on the materialized DB
    # ????? PERCHE' ????? filter_dataset ha senso solo se h multiple releases!!

    # following attributes used to be in a separate class VersionableDataSet
    '''
    an Instance belongs to a set of instances which are basically the same but with a different version
    root is the first instance of this set; root has root=self so that if I filter for root=smthng
    I get all of them including the root
    WE REFER TO SUCH SET AS THE "version set"
    '''
    root = models.ForeignKey('self', related_name='versions', null=True, blank=True)
    # http://semver.org/
    version_major = models.IntegerField(null=True, blank=True)
    version_minor = models.IntegerField(null=True, blank=True)
    version_patch = models.IntegerField(null=True, blank=True)
    version_description = models.CharField(max_length=2000L, default="")
    # dataset_date is the date of the release of the dataset; e.g. 
    dataset_date = models.DateTimeField(auto_now_add=True)
    # version_date is the date this version has been released in the OKS
    version_date = models.DateTimeField(auto_now_add=True)
    '''
    Assert: If self.dataset_structure.multiple_releases==False: at most one instance with the same root_version_id has version_released = True
    '''
    version_released = models.BooleanField(default=False)
    '''http://www.dcc.ac.uk/resources/how-guides/license-research-data 
        "The option to multiply license a dataset is certainly available to you if you hold all the rights 
        that pertain to the dataset"
    '''
    licenses = models.ManyToManyField("license.License")
    
    def get_instance(self, db_alias='default'):
        '''
        it returns the main instance of the structure i.e. the one with pk = self.entry_point_instance_id
        '''
        se_simple_entity = self.dataset_structure.entry_point.simple_entity
        actual_class = utils.load_class(se_simple_entity.module + ".models", se_simple_entity.name)
        return actual_class.objects.using(db_alias).get(pk=self.entry_point_instance_id)
    
    def get_instances(self, db_alias='ksm'):
        '''
        it returns the list of instances matching the filter criteria
        CHECK: sempre ksm? E' una view e quindi che senso ha andare su default dove ci sono anche le versioni vecchie?
        '''
        se_simple_entity = self.dataset_structure.entry_point.simple_entity
        actual_class = utils.load_class(se_simple_entity.module + ".models", se_simple_entity.name)
        q = eval("Q(" + self.filter_text + ")")
        return actual_class.objects.using(db_alias).filter(q)
    
    def get_instances_of_a_type(self, se, db_alias='ksm'):
        '''
        starting from the instances matching the filter criteria it returns the list of simple entities anywhere in the structure of the se type
        '''
        t = self.dataset_structure.navigate(self, "", "navigate_helper_list_by_type")
        if se in t.keys():
            return t[se]
        else:
            return None
    
    def serialize_with_actual_instance(self, format='XML', force_external_reference=False):
        '''
        DataSet should use GenericForeignKey https://docs.djangoproject.com/en/1.8/ref/contrib/contenttypes/
        instead of entry_point_instance_id; then serialize_with_actual_instance will be done with normal serialize

        parameters:
        TODO: force_external_reference if True ...
        '''
        serialized_head = ''
        format = format.upper()
        if format == 'XML':
            serialized_head = "<DataSet " + self.serialized_attributes(format) + " >"
        if format == 'JSON':
            serialized_head = ' { ' + self.serialized_attributes(format)
        comma = ""    
        if format == 'JSON':
            comma = ", "

        e_simple_entity = SimpleEntity.objects.get(name="DataSetStructure")
        temp_etn = StructureNode(simple_entity=e_simple_entity, external_reference=True, is_many=False, attribute="dataset_structure")
        serialized_head += comma + self.dataset_structure.serialize(temp_etn, exported_instances=[], format=format)
        
        ks_simple_entity = SimpleEntity.objects.get(name="KnowledgeServer")
        temp_etn = StructureNode(simple_entity=ks_simple_entity, external_reference=True, is_many=False, attribute="owner_knowledge_server")
        serialized_head += comma + self.owner_knowledge_server.serialize(temp_etn, exported_instances=[], format=format)
        
        ei_simple_entity = SimpleEntity.objects.get(name="DataSet")
        temp_etn = StructureNode(simple_entity=ei_simple_entity, external_reference=True, is_many=False, attribute="root")
        serialized_head += comma + self.root.serialize(temp_etn, exported_instances=[], format=format)

        if force_external_reference:
            self.dataset_structure.entry_point.external_reference = True

        if self.entry_point_instance_id:
            instance = self.get_instance()
            if format == 'XML':
                serialized_head += "<ActualInstance>" + instance.serialize(self.dataset_structure.entry_point, exported_instances=[], format=format) + "</ActualInstance>"
            if format == 'JSON':
                serialized_head += ', "ActualInstance" : { ' + instance.serialize(self.dataset_structure.entry_point, exported_instances=[], format=format) + " } "
        elif self.filter_text:
            instances = self.get_instances()
            if format == 'XML':
                serialized_head += "<ActualInstances>"
            if format == 'JSON':
                serialized_head += ', "ActualInstances" : [ '
            comma = ""
            for instance in instances:
                if format == 'XML':
                    serialized_head += "<ActualInstance>" + instance.serialize(self.dataset_structure.entry_point, exported_instances=[], format=format) + "</ActualInstance>"
                if format == 'JSON':
                    serialized_head += comma + ' { ' + instance.serialize(self.dataset_structure.entry_point, exported_instances=[], format=format) + " } "
                    comma = ', '
            if format == 'XML':
                serialized_head += "</ActualInstances>"
            if format == 'JSON':
                serialized_head += ' ] '
        if format == 'XML':
            serialized_tail = "</DataSet>"
        if format == 'JSON':
            serialized_tail = " }"
        return serialized_head + serialized_tail

    def from_xml_with_actual_instance(self, dataset_xml_stream):
        '''
        DataSet should use GenericForeignKey https://docs.djangoproject.com/en/1.8/ref/contrib/contenttypes/
        instead of entry_point_instance_id; then from_xml_with_actual_instance will be done with normal from_xml
        '''
        logger = utils.poor_mans_logger()
        # http://stackoverflow.com/questions/3310614/remove-whitespaces-in-xml-string 
        p = etree.XMLParser(remove_blank_text=True)
        elem = etree.XML(dataset_xml_stream, parser=p)
        dataset_xml_stream = etree.tostring(elem)
        xmldoc = minidom.parseString(dataset_xml_stream)
        
        dataset_xml = xmldoc.childNodes[0].childNodes[0]
        DataSetStructureURI = dataset_xml.getElementsByTagName("dataset_structure")[0].attributes["URIInstance"].firstChild.data

        # assert: the structure is present locally
        es = DataSetStructure.retrieve(DataSetStructureURI)
        self.dataset_structure = es
        
        try:
            with transaction.atomic():
                actual_instances_xml = []
                if es.is_a_view:
                    # I have a list of actual instances
                    for instance_xml in dataset_xml.getElementsByTagName("ActualInstances")[0].childNodes:
                        actual_instances_xml.append(instance_xml.childNodes[0])
                else:
                    # I create the actual instance
                    actual_instances_xml.append(dataset_xml.getElementsByTagName("ActualInstance")[0].childNodes[0])
                actual_class = utils.load_class(es.entry_point.simple_entity.module + ".models", es.entry_point.simple_entity.name)
                for actual_instance_xml in actual_instances_xml:
                    # already imported ?
                    actual_instance_URIInstance = actual_instance_xml.attributes["URIInstance"].firstChild.data
                    try:
                        actual_instance = actual_class.retrieve(actual_instance_URIInstance)
                        # it is already in this database; ?????I return the corresponding DataSet
#?????                        return DataSet.objects.get(dataset_structure=es, entry_point_instance_id=actual_instance_on_db.pk)
                    except:  # I didn't find it on this db, no problem
                        actual_instance = actual_class()
                        actual_instance.from_xml(actual_instance_xml, es.entry_point, insert=True)
                        # from_xml saves actual_instance on the database
                
                # I create the DataSet if not already imported
                dataset_URIInstance = dataset_xml.attributes["URIInstance"].firstChild.data
                try:
                    dataset_on_db = DataSet.retrieve(dataset_URIInstance)
                    if not es.is_a_view:
                        # actual_instance.pk changes during import as we have "insert = True" and the pk is set to None
                        dataset_on_db.entry_point_instance_id = actual_instance.pk
                        dataset_on_db.save()
                    return dataset_on_db
                except:  # I didn't find it on this db, no problem
                    # In the next call the KnowledgeServer owner of this DataSet must exist
                    # So it must be imported while subscribing; it is imported by this very same method
                    # Since it is in the actual instance the next method will find it
                    self.from_xml(dataset_xml, self.shallow_dataset_structure().entry_point, insert=True)
                    if not es.is_a_view:
                        # actual_instance.pk changes during import as we have "insert = True" and the pk is set to None
                        self.entry_point_instance_id = actual_instance.pk
                        self.save()
        except Exception as ex:
            print (ex.message)
            raise ex
        return self

    def new_version(self, version_major=None, version_minor=None, version_patch=None, version_description="", version_date=None):
        '''
        DATABASE: it is invoked only on default database as record go to the materialized one only
                  via the set_released method
        It creates new records for each record in the whole structure excluding extenal references
        version_released is set to False
        It creates a new DataSet and returns it
        
        '''
        if version_major == None or version_minor == None or version_patch == None:
            # if the version is not fully specified the least increase is chosen
            version_major = self.version_major
            version_minor = self.version_minor
            version_patch = self.version_patch + 1
        else:
            # it needs to be a greater version number
            message = "Trying to create a new version with an older version number."
            if version_major < self.version_major:
                raise Exception(message)
            else:
                if version_major == self.version_major and version_minor < self.version_minor:
                    raise Exception(message)
                else:
                    if version_major == self.version_major and version_minor == self.version_minor and version_patch < self.version_patch:
                        raise Exception(message)
        try:
            with transaction.atomic():
                instance = self.get_instance().new_version(self.dataset_structure.entry_point, processed_instances={})
                new_ei = DataSet()
                new_ei.version_major = version_major
                new_ei.version_minor = version_minor
                new_ei.version_patch = version_patch
                new_ei.owner_knowledge_server = KnowledgeServer.this_knowledge_server('default')
                new_ei.dataset_structure = self.dataset_structure
                new_ei.root = self.root
                new_ei.entry_point_instance_id = instance.id
                new_ei.version_description = version_description
                new_ei.workflow = self.workflow
                new_ei.current_status = self.current_status
                if version_date:
                    new_ei.version_date = version_date
                new_ei.save()
        except Exception as e:
            print (str(e))
        return new_ei
    
    def get_state(self):
        '''
        Three implicit states: working, released, obsolete  
         -  working: the latest version where version_released = False
         -  released: the one with version_released = True
         -  obsolete: all the others
        '''
        if self.version_released:
            return "released"
        version_major__max = self.__class__.objects.all().aggregate(Max('version_major'))['version_major__max']
        if self.version_major == version_major__max:
            version_minor__max = self.__class__.objects.filter(version_major=version_major__max).aggregate(Max('version_minor'))['version_minor__max']
            if self.version_minor == version_minor__max:
                version_patch__max = self.__class__.objects.filter(version_major=version_major__max, version_minor=version_minor__max).aggregate(Max('version_patch'))['version_patch__max']
                if self.version_patch == version_patch__max:
                    return "working"
        return "obsolete"
        
    def set_version(self, version_major=0, version_minor=1, version_patch=0):
        self.version_major = version_major
        self.version_minor = version_minor
        self.version_patch = version_patch

    def materialize_dataset(self):
        '''
        if this dataset is a view then I have imported it and need to materialize it with all its instances
        if it is not a view it will have just one instance
        '''
        try:
            if self.dataset_structure.is_a_view:
                instances = self.get_instances(db_alias='default')
            else:
                instances = []
                instances.append(self.get_instance(db_alias='default'))
            for instance in instances:
                m_existing = instance.__class__.objects.using('ksm').filter(URI_imported_instance=instance.URI_imported_instance)
                if len(m_existing) == 0:
                    instance.materialize(self.dataset_structure.entry_point, processed_instances=[])
            m_existing = DataSet.objects.using('ksm').filter(URI_imported_instance=self.URI_imported_instance)
            if len(m_existing) == 0:
                self.materialize(self.shallow_dataset_structure().entry_point, processed_instances=[])
            # end of transaction
        except Exception as ex:
            raise ex
            print ("materialize_dataset (" + self.description + "): " + str(ex))
        
        
    def set_released(self):
        '''
        Sets this version as the (only) released (one)
        It materializes data and the DataSet itself
        It triggers the generation of events so that subscribers to relevant datasets can get the notification
        '''
        try:
            with transaction.atomic():
                currently_released = None
                if not self.dataset_structure.multiple_releases:
                    # There cannot be more than one released? I set the others to False
                    try:
                        currently_released = self.root.versions.get(version_released=True)
                        if currently_released.pk != self.pk:
                            currently_released.version_released = False
                            currently_released.save()
                        previously_released = currently_released
                    except:
                        print("DataSet.set_released couldn't find a released version.")
                        pass  # not found
                # this one is released now
                self.version_released = True
                self.save()
                # MATERIALIZATION Now we must copy newly released self to the materialized database
                # I must check whether it is already materialized so that I don't do it twice
                m_existing = DataSet.objects.using('ksm').filter(URIInstance=self.URIInstance)
                if len(m_existing) == 0:
                    instance = self.get_instance()
                    materialized_instance = instance.materialize(self.dataset_structure.entry_point, processed_instances=[])
                    materialized_self = self.materialize(self.shallow_dataset_structure().entry_point, processed_instances=[])
                    # the id should already be the same; maybe autogeneration strategies on different dbms could ... 
                    materialized_self.entry_point_instance_id = materialized_instance.id
                    materialized_self.save()
                    if not self.dataset_structure.multiple_releases:
                        # if there is only a materialized release I must set root to self otherwise deleting the 
                        # previous version will delete this as well
                        materialized_self.root = materialized_self
                        materialized_self.save()
                        # now I can delete the old dataset (if any) as I want just one release (multiple_releases == false)
                        if currently_released and currently_released.pk != self.pk:
                            materialized_previously_released = DataSet.objects.using('ksm').get(URIInstance=previously_released.URIInstance)
                            materialized_previously_released.delete_entire_dataset()
                    
                    # If I own this DataSet then I create the event for notifications
                    # releasing a dataset that I do not own makes no sense; in fact when I create a new version of
                    # a dataset that has a different owner, the owner is set to this oks
                    this_ks = KnowledgeServer.this_knowledge_server()
                    if self.owner_knowledge_server.URIInstance == this_ks.URIInstance:
                        # TODO: in the future this task must be run asynchronously
                        e = Event()
                        e.dataset = self
                        e.type = "New version"
                        e.save()
                        '''#157 now I need to generate events for views
                        I shall navigate the release structure
                        Creating a set of lists, one list per each kind of SimpleEntity I encounter
                        Each list contains the instances without repetitions
                        Then for each list I find each DataSetStructure that contains a node of the SimpleEntity
                        For each DataSet with that structure that is a view I test whether at least one of the
                        instances on the list is also in the dataset (also I must check if any is no longer there!)
                        If so I generate the event for that dataset.
                        To check if one is no longer there I must generate the same lists also for previously_released
                        and then compare the lists after applying the criteria of the view

                        '''
                        released_instances_list = self.dataset_structure.navigate(self, "", "navigate_helper_list_by_type")
                        if not self.dataset_structure.multiple_releases:
                            previously_released_instances_list = previously_released.dataset_structure.navigate(self, "", "navigate_helper_list_by_type")
                        # I assume the list of keys of the above lists is the same, e.g. the dataset_structure has not changed
                        # keys are simpleentities
                        for se in released_instances_list.keys():
                            '''
                            '   if multiple_releases all the newly released instances can affect a view
                            '   else we must compare currently and previously released
                            '   I must create a list of
                            '    - all those that are in current but not in previous
                            '    - all those that are in previous but not in current
                            '    - all those that are in both but have changed 
                                        changed means attribute but TODO:also their relationships!!!
                            '''
                            if not self.dataset_structure.multiple_releases:
                                #     - all those that are in current but not in previous
                                current_not_previous = list(i for i in released_instances_list[se] if i.URI_previous_version not in list(i.URIInstance for i in previously_released_instances_list[se]))
                                #    - all those that are in previous but not in current
                                previous_not_current = list(i for i in previously_released_instances_list[se] if i.URIInstance not in list(i.URI_previous_version for i in released_instances_list[se]))
                                #    - all those that are in both but have changed 
                                current_changed = []
                                previous_changed = []
                                previous_and_current = list(i for i in previously_released_instances_list[se] if i.URIInstance in list(i.URI_previous_version for i in released_instances_list[se]))
                                for previous_instance in previous_and_current:
                                    current_instance = list(i for i in released_instances_list[se] if i.URI_previous_version == previous_instance.URIInstance)[0]
                                    if not SimpleEntity.compare(current_instance, previous_instance):
                                        current_changed.append(current_instance)
                                        previous_changed.append(previous_instance)
                            else: # CHECK: è già una lista?
                                current = released_instances_list[se]
                            # for each simple entity I must find the list of all structures of type view the contain
                            # at least a node of that type;
                            structure_views = se.dataset_types(is_shallow=False, is_a_view=True, external_reference=False)
                            for sv in structure_views:
                                # for each of them I find all the actual datasets
                                dataset_views = DataSet.objects.filter(dataset_structure = sv)
                                for dv in dataset_views:
                                    # instances of type se within the structure of the dataset
                                    t = dv.get_instances_of_a_type(se)
                                    generate_event = False
                                    if self.dataset_structure.multiple_releases:
                                        generate_event = (len(SimpleEntity.intersect_list(t, current)) > 0)
                                    else:
                                        generate_event = (len(SimpleEntity.intersect_list(t, (current_not_previous + previous_not_current + current_changed + previous_changed))) > 0)
                                    if generate_event:
                                        e = Event()
                                        e.dataset = dv
                                        e.type = "New version"
                                        e.save()
                    # end of transaction
        except Exception as ex:
            print ("set_released (" + self.description + "): " + str(ex))
    
    def delete_entire_dataset(self):
        '''
        Navigating the structure deletes each record in the entire dataset obviously excluding external references
        Then it deletes self
        '''
        # TODO: add transaction
        instance = self.get_instance('ksm')
        instance.delete_children(self.dataset_structure.entry_point)
        instance.delete()
        self.delete()
        
    def get_latest(self, released=None):
        '''
        gets the latest version starting from any DataSet in the version set
        it can be either released or not    if released is None:
        if released == True: the latest released one
        if released == False: the latest unreleased one
        '''
        if released is None:  # I take the latest regardless of the fact that it is released or not
            version_major__max = DataSet.objects.filter(root=self.root).aggregate(Max('version_major'))['version_major__max']
            version_minor__max = DataSet.objects.filter(root=self.root, version_major=version_major__max).aggregate(Max('version_minor'))['version_minor__max']
            version_patch__max = DataSet.objects.filter(root=self.root, version_major=version_major__max, version_minor=version_minor__max).aggregate(Max('version_patch'))['version_patch__max']
        else:  # I filter according to released
            version_major__max = DataSet.objects.filter(version_released=released, root=self.root).aggregate(Max('version_major'))['version_major__max']
            version_minor__max = DataSet.objects.filter(version_released=released, root=self.root, version_major=version_major__max).aggregate(Max('version_minor'))['version_minor__max']
            version_patch__max = DataSet.objects.filter(version_released=released, root=self.root, version_major=version_major__max, version_minor=version_minor__max).aggregate(Max('version_patch'))['version_patch__max']
        return DataSet.objects.get(root=self.root, version_major=version_major__max, version_minor=version_minor__max, version_patch=version_patch__max)
   
class UploadedFile(models.Model):
    '''
    Used to save uploaded xml file so that it can be later retrieved and imported
    '''
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class Event(SerializableSimpleEntity):
    '''
    Something that has happened to a specific instance and you want to get notified about; 
    so you can subscribe to a type of event for a specific data set / DataSet
    '''
    # The DataSet
    dataset = models.ForeignKey(DataSet)
    # the event type
    type = models.CharField(max_length=50, default="New version")
    # when it was fired
    timestamp = models.DateTimeField(auto_now_add=True)
    # if all notifications have been prepared e.g. relevant Notification instances are saved
    processed = models.BooleanField(default=False)

class SubscriptionToThis(SerializableSimpleEntity):
    '''
    The subscriptions other systems do to my data
    '''
    root_URIInstance = models.CharField(max_length=2000L)
    # where to send the notification; remote_url, in the case of a KS, will be something like http://rootks.thekoa.org/notify
    # the actual notification will have the URIInstance of the DataSet and the URIInstance of the EventType
    remote_url = models.CharField(max_length=200L)
    # I send a first notification that can be used to get the data the first time
    first_notification_prepared = models.BooleanField(default=False)

class Notification(SerializableSimpleEntity):
    '''
    When an event happens for an instance, for each corresponding subscription
    I create a  Notification; cron will send it and change its status to sent
    '''
    event = models.ForeignKey(Event)
    sent = models.BooleanField(default=False)
    remote_url = models.CharField(max_length=200L)

class SubscriptionToOther(SerializableSimpleEntity):
    '''
    The subscriptions I make to other systems' data
    '''
    # The URIInstance I am subscribing to 
    URI = models.CharField(max_length=200L)
    root_URIInstance = models.CharField(max_length=200L)

class NotificationReceived(SerializableSimpleEntity):
    '''
    When I receive a notification it is stored here and processed asynchronously in cron 
    '''
    # URI to fetch the new data
    URL_dataset = models.CharField(max_length=200L)
    URL_structure = models.CharField(max_length=200L)
    processed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class ApiReponse():
    '''
    
    '''
    def __init__(self, status="", message=""):
        self.status = status
        self.message = message
        
    def json(self):
        ret_str = '{ "status" : "' + self.status + '", "message" : "' + self.message + '"}'
        return ret_str
    
    def parse(self, json_response):
        decoded = json.loads(json_response)
        self.status = decoded['status']
        self.message = decoded['message']
        
class KsUri(object):
    '''
    This class is responsible for the good quality of all URIs generated by a KS
    in terms of syntax and for their coherent use throughout the whole application
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
        for format in utils.Choices.FORMAT:
            if self.clean_uri[-(len(format) + 1):].lower() == "/" + format:
                self.clean_uri = self.clean_uri[:-(len(format) + 1)]
                self.format = format

        # I check whether it's structure i well formed according to the GenerateURIInstance method
        self.is_sintactically_correct = False
        # not it looks something like: http://rootks.thekoa.org/entity/SimpleEntity/1
        self.clean_parsed = urlparse(self.clean_uri)
        self.scheme = ""
        for scheme in utils.Choices.SCHEME:
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
                temp_path = temp_path[temp_path.find('/') + 1:]
                # 'SimpleEntity/1'
                if temp_path.find('/'):
                    self.class_name = temp_path[:temp_path.find('/')]
                    temp_path = temp_path[temp_path.find('/') + 1:]
                    print(temp_path)
                    if temp_path.find('/') < 0:
                        self.pk_value = temp_path
                        self.is_sintactically_correct = True

    def base64(self):
        return base64.encodestring(self.uri).replace('\n', '')
        
    def __repr__(self):
        return self.scheme + '://' + self.netloc + '/' + self.namespace + '/' + self.class_name + '/' + str(self.pk_value)
    
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
        # I search on this database
        #  on URIInstance
            
