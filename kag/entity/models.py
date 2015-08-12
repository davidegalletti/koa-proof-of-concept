# -*- coding: utf-8 -*-

from datetime import datetime
from random import randrange, uniform

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver

from userauthorization.models import KUser
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
    URI_previous_version = models.CharField(max_length=2000L, null = True, blank=True)
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
        there is no EntityStructure? Then I use the app name
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
                if se.entity_structure != None:
                    namespace = se.entity_structure.namespace
            except:
                name = self.__class__.__name__
                id_field = "pk"
            return this_ks.uri() + "/" + namespace + "/" + name + "/" + str(getattr(self, id_field))
        except Exception as es:
            print ("Exception 'generate_URIInstance' " + self.__class__.__name__ + "." + str(self.pk) + ":" + es.message)
            return ""
    
    def get_simple_entity(self, class_name = "", db_alias = 'ksm'):
        '''
        *** method that works BY DEFAULT on the materialized database ***
        finds the instance of class SimpleEntity where the name corresponds to the name of the class of self
        '''
        if class_name == "":
            return SimpleEntity.objects.using(db_alias).get(name=self.__class__.__name__)
        else:
            return SimpleEntity.objects.using(db_alias).get(name=class_name)

    def entities(self):
        '''
        Lists the entities associated whose entry point is the instance of class SimpleEntity corresponding to the class of self
        '''
        return EntityStructure.objects.filter(entry_point__simple_entity=self.get_simple_entity())

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
     
    def serialized_URI_SE(self, format = 'XML'):
        if format == 'XML':
            return ' URISimpleEntity="' + self.get_simple_entity().URIInstance + '" '  
        if format == 'JSON':
            return ' "URISimpleEntity" : "' + self.get_simple_entity().URIInstance + '" '
        
    def serialized_attributes(self, format = 'XML'):
        attributes = ""
        comma = ""
        for key in self._meta.fields:
            if key.__class__.__name__ != "ForeignKey":
                if format == 'XML':
                    attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'  
                if format == 'JSON':
                    attributes += comma + '"' + key.name + '" : "' + str(getattr(self, key.name)) + '"'
                    comma = ", "
        return attributes

    def shallow_entity_structure(self, db_alias = 'default'):
        '''
        It creates an EntityStructure, saves it on the database and returns it.
        if a user wants to serialize a SerializableSimpleEntity without passing an EntityStructure
        I search for an EntityStructure with is_shallow=True; if I can't find it I create it and save it
        for future use
        '''
        try:
            se = EntityStructure.objects.using(db_alias).get(entry_point__simple_entity = self.get_simple_entity(), is_shallow = True)
        except:
            se = EntityStructure()
            se.is_shallow = True
            se.name = self.__class__.__name__ + " (shallow)"
            se.simple_entity = self.get_simple_entity()
            se.entry_point = self.shallow_entity_structure_node(db_alias)
            se.save()
            se.URIInstance = se.generate_URIInstance()
            se.save(using=db_alias)
        return se 
        
    def shallow_entity_structure_node(self, db_alias = 'default'):
        '''
        it creates an EntityStructureNode used to serialize (to_xml) self. It has the SimpleEntity 
        and references to ForeignKeys and ManyToMany
        '''
        etn = EntityStructureNode()
        etn.simple_entity = self.get_simple_entity() 
        etn.external_reference=False
        etn.is_many=False
        etn.save(using=db_alias)
        etn.child_nodes = []
        for fk in self.foreign_key_attributes():
            etn_fk = EntityStructureNode()
            if getattr(self, fk) is None:
                # the attribute is not set so I can't get its __class__.__name__ and I take it from the model
                class_name = self._meta.get_field(fk).rel.model.__name__
                etn_fk.simple_entity = self.get_simple_entity(class_name)
            else:
                etn_fk.simple_entity = getattr(self, fk).get_simple_entity()
            etn_fk.external_reference=True
            etn_fk.attribute = fk
            etn_fk.is_many=False
            etn_fk.save(using=db_alias)
            etn.child_nodes.add(etn_fk)
        for rm in self.related_manager_attributes():
            #TODO: shallow_entity_structure_node: implement self.related_manager_attributes case
            pass
        for mrm in self.many_related_manager_attributes():
            #TODO: shallow_entity_structure_node: implement self.many_related_manager_attributes case
            pass
        etn.save(using=db_alias)
        return etn

    def serialize(self, etn = None, exported_instances = [], format = 'XML'):
        '''
        format: {'XML' | 'JSON'}

            If I have already exported this instance I don't want to duplicate all details hence I just export it's URIInstance, 
            name and SimpleEntity URI. Then I need to add an attribute so that when importing it I will recognize that its details
            are somewhere else in the file
            <EntityStructureNode URISimpleEntity="....." URIInstance="...." attribute="...." KS_TAG_WITH_NO_DATA=""
            the TAG "KS_TAG_WITH_NO_DATA" is used to mark the fact that the details of this SimpleEntity are somewhere else in the file
        '''
        format = format.upper()
        serialized = ""
        # if there is no etn I export just this object creating a shallow EntityStructure 
        if etn is None:
            etn = self.shallow_entity_structure().entry_point
        if etn.is_many:
            # the attribute correspond to a list of instances of the SimpleEntity 
            tag_name = etn.simple_entity.name
        else:
            tag_name = self.__class__.__name__ if etn.attribute == "" else etn.attribute
        # already exported, I just export a short reference with the URI_Instance
        if self.URIInstance and self.URIInstance in exported_instances and etn.simple_entity.name_field:
            if format == 'XML':
                xml_name = " " + etn.simple_entity.name_field + "=\"" + getattr(self, etn.simple_entity.name_field) + "\""
                return '<' + tag_name + ' KS_TAG_WITH_NO_DATA=\"\"' + self.serialized_URI_SE(format) + xml_name + ' URIInstance="' + self.URIInstance + '"/>'  
            if format == 'JSON':
                xml_name = ' "' + etn.simple_entity.name_field + '" : "' + getattr(self, etn.simple_entity.name_field) + '"'
                if etn.is_many:
                    return ' { "KS_TAG_WITH_NO_DATA" : \"\", ' + self.serialized_URI_SE(format) + ", " + xml_name + ', "URIInstance": "' + self.URIInstance + '"} '
                else:
                    return '"' + tag_name + '" : { "KS_TAG_WITH_NO_DATA" : \"\", ' + self.serialized_URI_SE(format) + ", " + xml_name + ', "URIInstance": "' + self.URIInstance + '"}'  
        
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
            
    def new_version(self, etn, processed_instances, parent = None):
        '''
        invoked by EntityInstance.new_version that wraps it in a transaction
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
            return self.__class__.objects.get(URIInstance = processed_instances[str(self.URIInstance)])
        
        new_instance = self.__class__()
        if parent:
#           I have a parent; let's set it
            field_name = SerializableSimpleEntity.get_parent_field_name(parent, etn.attribute)
            if field_name:
                setattr(new_instance, field_name, parent)
                
        for en_child_node in etn.child_nodes.all():
            if en_child_node.attribute in self.foreign_key_attributes():
                #not is_many
                child_instance = eval("self." + en_child_node.attribute)
                new_child_instance = child_instance.new_version(en_child_node, processed_instances)
                setattr(new_instance, en_child_node.attribute, new_child_instance) #the parameter "parent" shouldn't be necessary in this case as this is a ForeignKey
                
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
                #not is_many
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
        
    def materialize(self, etn, processed_instances, parent = None):
        '''
        invoked by EntityInstance.set_released that wraps it in a transaction
        it recursively invokes itself to copy the full structure to the materialized DB
        
        ASSERTION: URIInstance remains the same on the materialized database
        
        processed_instances is a list of processed URIInstance 
        '''

        if etn.external_reference:
            return self
            child_instance = eval("self." + etn.attribute)
            # e.g. EntityInstance.root is a self relationship often set to self; I am materializing self
            # so I don't have it; I return self; I could probably do the same also in the other case
            # because what actually counts for Django is the pk
            if self == child_instance:
                return self
            # if it is an external reference I do not have to materialize it
            # I expect it to be already materialized so I try to return that instance
            try:
                return self.__class__.objects.using('ksm').get(URIInstance=self.URIInstance)
            except Exception as ex:
                new_ex = Exception("SerializableSimpleEntity.materialize: self.URIInstance: " + self.URIInstance + " searching it on ksm: " + ex.message)
                raise ex

        if self.URIInstance and str(self.URIInstance) in processed_instances:
            # already materialized it, I return that one 
            return self.__class__.objects.using('ksm').get(URIInstance = self.URIInstance)
        
        new_instance = self.__class__()
        if parent:
#           I have a parent; let's set it
            field_name = SerializableSimpleEntity.get_parent_field_name(parent, etn.attribute)
            if field_name:
                setattr(new_instance, field_name, parent)
                
        for en_child_node in etn.child_nodes.all():
            if en_child_node.attribute in self.foreign_key_attributes():
                #not is_many
                # if they are nullable I do nothing
                try:
                    child_instance = getattr(self, en_child_node.attribute)
                    new_child_instance = child_instance.materialize(en_child_node, processed_instances)
                    setattr(new_instance, en_child_node.attribute, new_child_instance) #the parameter "parent" shouldn't be necessary in this case as this is a ForeignKey
                except Exception as ex:
                    print("SerializableSimpleEntity.materialize: " + self.__class__.__name__ + " " + str(self.pk) + " attribute \"" + en_child_node.attribute + "\" " + ex.message)
        for key in self._meta.fields:
            if key.__class__.__name__ != "ForeignKey" and self._meta.pk != key:
                setattr(new_instance, key.name, eval("self." + key.name))
        
        # I have added all attributes corresponding to ForeignKey, I can save it so that I can use it as a parent for the other attributes
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
                    #not is_many
                    child_instance = eval("self." + en_child_node.attribute)
                    new_child_instance = child_instance.materialize(en_child_node, processed_instances, self)
                    setattr(new_instance, en_child_node.attribute, new_child_instance)
        
        new_instance.save(using='ksm')
        # after saving
        processed_instances.append(new_instance.URIInstance)
        return new_instance
        
    def delete_children(self, etn, parent = None):
        '''
        invoked by EntityInstance.delete_entire_dataset that wraps it in a transaction
        it recursively invokes itself to delete children's children; self is in the 
        materialized database
        
        It is invoked only if EntityInstance.entity_structure.multiple_releases = False
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
                    #not is_many
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
                #I NEED TO LIST TODO:ALL THE RELATIONSHIPS POINTING AT THIS MODEL
                for rel_key in self._meta.fields_map.keys():
                    rel = self._meta.fields_map[rel_key]
                    if rel.__class__.__name__ == 'ManyToOneRel':
                        related_name =rel.related_name
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
                raise Exception('NOT IMPLEMENTED in SerializableSimpleEntity.delete_children: mapping between different versions: URIInstance "' + self.URIInstance + '" has ' +str(len(new_instances)) + ' materialized records that have this as URI_previous_version.') 
        except Exception as e:
            print(e.message)
            
    @staticmethod
    def simple_entity_from_xml_tag(xml_child_node):
        URIInstance = xml_child_node.attributes["URISimpleEntity"].firstChild.data
        try:
            se = SimpleEntity.objects.get(URIInstance = URIInstance)
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
            
            TODO: When importing an EntityInstance from another KS, its root will point to either self or to an EntityInstance
            that is on the other KS; in the latter case I search for this root EntityInstance using the field 
            SerializableSimpleEntity.URI_imported_instance; if I find it I set root to point to it otherwise
            I set it to self.
            '''
            #estrarre l'url del KS
            ks_url = ""
            #encode di URIInstance
            URIInstance_base64 = ""
            #wget ks_url + "/ks/api/simple_entity_definition/" + URIInstance_base64
            raise Exception("NOT IMPLEMENTED in simple_entity_from_xml_tag: get SimpleEntity from appropriate KS.")
        return se

    @staticmethod
    def retrieve(actual_class, URIInstance, retrieve_externally):
        '''
        It returns an instance of a SerializableSimpleEntity stored in this KS
        It searches first on the URIInstance field (e.g. is it already an instance of this KS? ) 
        It searches then on the URI_imported_instance field (e.g. has is been imported in this KS from the same source? )
        It fetches the instance from the source as it is not in this KS yet 
        '''
        actual_instance = None
        try:
            actual_instance = actual_class.objects.get(URIInstance=URIInstance)
        except:
            try:
                actual_instance = actual_class.objects.get(URI_imported_instance=URIInstance)
            except:
                if retrieve_externally:
                    #TODO: It fetches the instance from the source as it is not in this KS yet
                    raise Exception("NOT IMPLEMENTED: It fetches the instance from the source as it is not in this KS yet")
                else:
                    raise Exception("Can't find instance with URI: " + URIInstance)
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

    def from_xml(self, xmldoc, entity_structure_node, insert=True, parent=None):
        '''
        from_xml gets from xmldoc the attributes of self and saves it; it searches for child nodes according
        to what the entity_structure_node says, creates instances of child objects and call itself recursively
        Every tag corresponds to a SimpleEntity, hence it
            contains a tag URISimpleEntity which points to the KS managing the SimpleEntity definition
        
        Each SerializableSimpleEntity has URIInstance and URI_imported_instance attributes. 
        
        external_reference
            the first SimpleEntity in the XML cannot be marked as an external_reference in the entity_structure_node
            from_xml doesn't get called recursively for external_references which are sought in the database
            or fetched from remote KS, so I assert self it is not an external reference
        
        '''
        field_name = ""
        if parent:
#           I have a parent; let's set it
            field_name = SerializableSimpleEntity.get_parent_field_name(parent, entity_structure_node.attribute)
            if field_name:
                setattr(self, field_name, parent)
        '''
        Some TAGS have no data (attribute KS_TAG_WITH_NO_DATA is present) because the instance they describe
        is present more than once in the XML file and the export doesn't replicate data; hence either
           I have it already in the database so I can load it
        or
           I have to save this instance but I will find its attribute later in the imported file
        '''
        try:
            xmldoc.attributes["KS_TAG_WITH_NO_DATA"]
            # if the TAG is not there an exception will be raised and the method will continue and expect to find all data
            module_name = entity_structure_node.simple_entity.module
            actual_class = utils.load_class(module_name + ".models", entity_structure_node.simple_entity.name) 
            try:
                instance = SerializableSimpleEntity.retrieve(actual_class, xmldoc.attributes["URIInstance"].firstChild.data, False)
                # It's in the database; I just need to set its parent; data is either already there or it will be updated later on
                if parent:
                    field_name = SerializableSimpleEntity.get_parent_field_name(parent, entity_structure_node.attribute)
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
                        print("Error in KS_TAG_WITH_NO_DATA TAG setting attribute URIInstance for instance of class " + self.__class__.__name__)
            #let's exit, nothing else to do, it's a KS_TAG_WITH_NO_DATA
            return
             
        except:
            #nothing to do, there is no KS_TAG_WITH_NO_DATA attribute
            pass
        for key in self._meta.fields:
            '''
              let's setattr the other attributes
              that are not ForeignKey as those are treated separately
              and is not the field_name pointing at the parent as it has been already set
            '''
            if key.__class__.__name__ != "ForeignKey" and (not parent or key.name != field_name):
                try:
                    if key.__class__.__name__ == "BooleanField":
                        setattr(self, key.name, xmldoc.attributes[key.name].firstChild.data.lower() == "true") 
                    else:
                        setattr(self, key.name, xmldoc.attributes[key.name].firstChild.data)
                except:
                    print("Error extracting from xml \"" + key.name + "\" for object of class \"" + self.__class__.__name__ + "\" with ID " + str(self.id))
        try:
            # URI_imported_instance stores the URIInstance from the XML
            self.URI_imported_instance = xmldoc.attributes["URIInstance"].firstChild.data
        except:
            # there's no URIInstance in the XML; it doesn't matter
            pass
        # I must set foreign_key child nodes BEFORE SAVING self otherwise I get an error for ForeignKeys not being set
        for en_child_node in entity_structure_node.child_nodes.all():
            if en_child_node.attribute in self.foreign_key_attributes():
                try:
                    # ASSERT: in the XML there is exactly one child tag
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
                        try:
                            # let's search it in the database
                            instance = SerializableSimpleEntity.retrieve(actual_class, xml_child_node.attributes["URIInstance"].firstChild.data, True)
                        except ObjectDoesNotExist:
                            # TODO: if it is not there I fetch it using it's URI and then create it in the database
                            pass
                        except:
                            raise Exception("\"" + module_name + ".models " + se.name + "\" has no instance with URIInstance \"" + xml_child_node.attributes["URIInstance"].firstChild.data)
                    else:
                        if insert:
                            # the user asked to "always create", let's create the instance
                            instance = actual_class()
                        else:
                            try:
                                instance = SerializableSimpleEntity.retrieve(actual_class, xml_child_node.attributes["URIInstance"].firstChild.data, False)
                            except:
                                # didn't find it; I create the instance anyway
                                instance = actual_class()
                        # from_xml takes care of saving instance with a self.save() at the end
                        instance.from_xml(xml_child_node, en_child_node, insert) #the fourth parameter, "parent" shouldn't be necessary in this case as this is a ForeignKey
                    setattr(self, en_child_node.attribute, instance)
                except Exception as ex:
                    print (ex.message)
                    #raise Exception("### add relevant message: from_xml")
                 
        # I have added all attributes corresponding to ForeignKey, I can save it so that I can use it as a parent for the other attributes
        self.save()
        # from_xml can be invoked on an instance retrieved from the database (where URIInstance is set)
        # or created on the fly (and URIInstance is not set); in the latter case, only now I can generate URIInstance
        # as I have just saved it and I have a local ID
        
        # TODO: now the generate_URIInstance should be invoked by the post_save
        if not self.URIInstance:
            self.URIInstance = self.generate_URIInstance()
            self.save()
 
        for en_child_node in entity_structure_node.child_nodes.all():
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
                            instance = SerializableSimpleEntity.retrieve(actual_class, xml_child_node.attributes["URIInstance"].firstChild.data, True)
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
                                    instance = SerializableSimpleEntity.retrieve(actual_class, xml_child_node.attributes["URIInstance"].firstChild.data, False)
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
                        instance = SerializableSimpleEntity.retrieve(actual_class, xml_child_node.attributes["URIInstance"].firstChild.data, True)
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
                                instance = SerializableSimpleEntity.retrieve(actual_class, xml_child_node.attributes["URIInstance"].firstChild.data, False)
                            except:
                                instance = actual_class()
                        instance.from_xml(xml_child_node, en_child_node, insert, self)
        
    class Meta:
        abstract = True

class DBConnection(models.Model):
    connection_string = models.CharField(max_length=255L)
    name = models.CharField(max_length=100L, null = True, blank=True)
    description = models.CharField(max_length=2000L, null = True, blank=True)

class Workflow(SerializableSimpleEntity):
    '''
    Is a list of WorkflowMethods; the work-flow is somehow abstract, its methods do not specify details of 
    the operation but just the statuses
    '''
    name = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    entity_structure = models.ForeignKey('EntityStructure', null = True, blank=True)
#     ASSERT: I metodi di un wf devono avere impatto solo su SimpleEntity contenute nell'EntityStructure

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

class WorkflowEntityInstance(models.Model):
    '''
    WorkflowEntityInstance
    '''
    workflow = models.ForeignKey(Workflow)
    current_status = models.ForeignKey(WorkflowStatus)
    class Meta:
        abstract = True

class WorkflowTransition(SerializableSimpleEntity):
    instance = models.ForeignKey("EntityInstance")
    workflow_method = models.ForeignKey('WorkflowMethod')
    notes = models.TextField()
    #TODO: non voglio null=True ma non so come gestire la migration nella quale mi chiede un default value 
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
    #urlparse terminology https://docs.python.org/2/library/urlparse.html
#     scheme e.g. { "http" | "https" }
    scheme = models.CharField(max_length=50L)
#     netloc e.g. "ks.thekoa.org"
    netloc = models.CharField(max_length=200L)
    
    organization = models.ForeignKey(Organization)
    def uri(self, encode_base64 = False):
        # "http://rootks.thekoa.org/"
        uri = self.scheme + "://" + self.netloc
        if encode_base64:
            uri = base64.encodestring(uri)
        return uri
    
    def run_cron(self):
        '''
        This method processes notifications received, generate notifications to be sent
        if events have occurred, ...
        '''
        pass
    @staticmethod
    def this_knowledge_server(db_alias = 'ksm'):
        '''
        *** method that works BY DEFAULT on the materialized database ***
        *** the reason being that only there "get(this_ks = True)" is ***
        *** guaranteed to return exactly one record                   ***
        when working on the default database we must first fetch it on the
        materialized; then, using the URIInstance we search it on the default
        because the URIInstance will be unique there
        '''
        materialized_ks = KnowledgeServer.objects.using('ksm').get(this_ks = True)
        if db_alias == 'default':
            return KnowledgeServer.objects.using('default').get(URIInstance = materialized_ks.URIInstance)
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
    description = models.CharField(max_length=2000L, default = "")
    table_name = models.CharField(max_length=255L, db_column='tableName', default = "")
    id_field = models.CharField(max_length=255L, db_column='idField', default = "id")
    name_field = models.CharField(max_length=255L, db_column='nameField', default = "name")
    description_field = models.CharField(max_length=255L, db_column='descriptionField', default = "description")
    connection = models.ForeignKey(DBConnection, null=True, blank=True)
    '''
    entity_structure attribute is not in NORMAL FORM! When not null it tells in which EntityStructure is this 
    SimpleEntity; a SimpleEntity must be in only one EntityStructure for version/state purposes! It can be in
    other EntityStructure that are used as views.
    '''
    entity_structure = models.ForeignKey("EntityStructure", null=True, blank=True)

class AttributeType(SerializableSimpleEntity):
    name = models.CharField(max_length=255L, blank=True)
    widgets = models.ManyToManyField('application.Widget', blank=True)

class Attribute(SerializableSimpleEntity):
    name = models.CharField(max_length=255L, blank=True)
    simple_entity = models.ForeignKey('SimpleEntity', null=True, blank=True)
    type = models.ForeignKey('AttributeType')
    def __str__(self):
        return self.simple_entity.name + "." + self.name

class EntityStructureNode(SerializableSimpleEntity):
    simple_entity = models.ForeignKey('SimpleEntity')
    # attribute is blank for the entry point
    attribute = models.CharField(max_length=255L, blank=True)
    # related_name "parent_entity_structure_node" is not used now
    child_nodes = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="parent_entity_structure_node")
    # if not external_reference all attributes are exported, otherwise only the id
    external_reference = models.BooleanField(default=False, db_column='externalReference')
    # is_many is true if the attribute correspond to a list of instances of the SimpleEntity
    is_many = models.BooleanField(default=False, db_column='isMany')

class EntityStructure(SerializableSimpleEntity):
    entity_structure_entity_structure_name = "EntityStructure-EntityStructureNode"
    simple_entity_entity_structure_name = "SimpleEntity-attributes"
    workflow_entity_structure_name = "Workflow-statuses"
    organization_entity_structure_name = "Organization-KnowledgeServer"
    '''
    Main idea behind the model: an Entity is not represented with a single class or a single 
    table in a database but it is usually represented using a collection of them: more than 
    one class and more than one table in the database. An Issue in a tracking system is an 
    EntityStructure; it has a list of notes that can be appended to it, it has a user who has created
    it, and many other attributes. The user does not belong just to this EntityStructure, hence it
    is a reference; the notes do belong to the issue. The idea is to map the set of tables
    in a (relational) database into entities so that our operations can handle this more
    generic EntityStructure that we are defining, composed with more than one SimpleEntity (in 
    more direct correspondence with a database table, SimpleEntity in our model). A simple
    entity can be in more than one EntityStructure; because, for instance, we might like to render/...
    .../export/... a subset of the simple entities of a complex entity.
    When we get to EntityInstance (which inherits from VersionableEntityInstance and 
    WorkflowEntityInstance) we must add a constraint because we want a unique way
    to know the version and the status of a simple instance: take the set of entities
    in the EntityStructure attribute of all instances of EntityInstance. In the graph of each
    EntityStructure, consider only the simple entities that are not references; the constraint
    is that each SimpleEntity must not be in the graph of more than one EntityStructure; otherwise
    it would be impossible to determine its version and status. In other words the entities
    used by EntityInstance must partition the E/R diagram of our database in graphs without
    any intersection. 
     
    An EntityStructure is a graph that defines a set of simple entities on which we can perform a task; 
    it has an entry point which is a Node e.g. an EntityStructure; from an instance of an EntityStructure we can use
    the "attribute" attribute from the corresponding EntityStructureNode to get the instances of
    the entities related to each of the child_nodes. An EntityStructure could, for example, tell
    us what to export to xml/json, ???????????????? what to consider as a "VersionableMultiEntity" (e.g. an
    instance of VersionableEntityInstance + an EntityStructure where the entry_point points to that instance)
    The name should describe its use ?????????????????
    
    Types of EntityStructure
    standard ones: used to define the structure of an EntityInstance
                   if a SimpleEntity is in one of them it cannot be in another one of them
    shallow      : created automatically to export a SimpleEntity
    view         : used for example to export a structure different from one of the above; it has no version information
    '''
    name = models.CharField(max_length=200L)
    description = models.CharField(max_length=2000L)
    '''
    an EntityStructure is shallow when it is automatically created to export a SimpleEntity; 
    is_shallow = True means that all foreignKeys and related attributes are external references
    '''
    is_shallow = models.BooleanField(default=False)
    '''
    an EntityStructure is a view if it is not used to determine the structure of an EntityInstance
    hence it is used for example to export some data
    '''
    is_a_view = models.BooleanField(default=False)
    '''
    the entry point of the structure; the class EntityStructureNode has then child_nodes of the same class 
    hence it defines the structure
    '''
    entry_point = models.ForeignKey('EntityStructureNode')
    '''
    when multiple_releases is true more than one instance get materialized
    otherwise just one; it defaults to False just not to make it nullable;
    a default is indicated as shallow structures are created without specifying it
    makes no sense when is_a_view
    '''
    multiple_releases = models.BooleanField(default=False)
    
    '''
    TODO: the namespace is defined in the organization owner of this EntityStructure
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

class EntityInstance(SerializableSimpleEntity):
    '''
    A data set / chunk of knowledge; its data structure is described by self.entity_structure
    The only Versionable object so far
    Serializable like many others 
    It has an owner KS which can be inferred by the URIInstance but it is explicitly linked 

    An EntityInstance is Versionable
    an Instance belongs to a set of instances which are basically the same but with a different version
    
    It will inherit from WorkflowEntityInstance when we will implement workflow features
    
    Relevant methods:
        new version: create new instances starting from entry point, following the nodes but those with external_reference=True
        set_released: it sets version_released True and it sets it to False for all the other instances of the same set
    '''
    owner_knowledge_server = models.ForeignKey(KnowledgeServer)

    # if the structure is intended to be a view there won't be any version information
    # assert entity_structure.is_a_view ===> root, version, ... == None
    entity_structure = models.ForeignKey(EntityStructure)

    # if it is a view a description might be useful
    description = models.CharField(max_length=2000L, default = "")
    
    # we have the ID of the instance because we do not know its class so we can't have a ForeignKey to an unknown class
    entry_point_instance_id = models.IntegerField(null=True, blank=True)

    # An alternative to the entry_point_instance_id is to have a filter to apply to the all the objects of type entry_point.instance
    # assert 
    #     filter_text != None ===> entry_point_instance_id == None
    #     entry_point_instance_id != None ===> filter_text == None
    # if entry_point_instance_id == None filter_text can be "" meaning that you have to take all of the entries without filtering them
    filter_text = models.CharField(max_length=200L, null=True, blank=True)

    # when the entry_point_instance_id is None (hence the structure is a view) I still might want to refer to a version for the data
    # that will be in my view; there might be data belongin to different versions matching the criteria in the filter text; to prevent
    # this I specify an EntityInstance (that has its own version) so that I will put in the view only those belonging to that version
    filter_entity_instance = models.ForeignKey('self', null=True, blank=True)
    # if filter_entity_instance is None then the view will filter on the materialized DB

    #following attributes used to be in a separate class VersionableEntityInstance
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
    version_description = models.CharField(max_length=2000L, default = "")
    version_date = models.DateTimeField(auto_now_add=True)
    '''
    Assert: If self.entity_structure.multiple_releases==False: at most one instance with the same root_version_id has version_released = True
    '''
    version_released = models.BooleanField(default=False)
    
    def get_instance(self, db_alias='default'):
        '''
        it returns the main instance of the structure i.e. the one with pk = self.entry_point_instance_id
        '''
        se_simple_entity = self.entity_structure.entry_point.simple_entity
        actual_class = utils.load_class(se_simple_entity.module + ".models", se_simple_entity.name)
        return actual_class.objects.using(db_alias).get(pk=self.entry_point_instance_id)
    
    def serialize_with_simple_entity(self, format = 'XML', force_external_reference=False):
        '''
        parameters:
        TODO: force_external_reference if True ...
        '''
        serialized_head = ''
        format = format.upper()
        if format == 'XML':
            serialized_head = "<EntityInstance namespace=\"" + self.entity_structure.namespace + "\" URIInstance=\"" + self.URIInstance + "\" VersionMajor=\"" + str(self.version_major) + "\" VersionMinor=\"" + str(self.version_minor) + "\" VersionPatch=\"" + str(self.version_patch) + "\" VersionReleased=\"" + str(self.version_released) + "\" VersionDescription=\"" + self.version_description + "\">"
        if format == 'JSON':
            serialized_head = ' { "namespace" : "' + self.entity_structure.namespace + '", "URIInstance" : "' + self.URIInstance + '", "VersionMajor" : "' + str(self.version_major) + '", "VersionMinor" : "' + str(self.version_minor) + '", "VersionPatch" : "' + str(self.version_patch) + '", "VersionReleased" : "' + str(self.version_released) + '", "VersionDescription" : "' + self.version_description + '" '
        comma = ""    
        if format == 'JSON':
            comma = ", "

        e_simple_entity = SimpleEntity.objects.get(name="EntityStructure")
        temp_etn = EntityStructureNode(simple_entity=e_simple_entity, external_reference=True, is_many=False, attribute = "entity_structure")
        serialized_head += comma + self.entity_structure.serialize(temp_etn, format = format)
        
        ks_simple_entity = SimpleEntity.objects.get(name="KnowledgeServer")
        temp_etn = EntityStructureNode(simple_entity=ks_simple_entity, external_reference=True, is_many=False, attribute = "owner_knowledge_server")
        serialized_head += comma + self.owner_knowledge_server.serialize(temp_etn, format = format)
        
        ei_simple_entity = SimpleEntity.objects.get(name="EntityInstance")
        temp_etn = EntityStructureNode(simple_entity=ei_simple_entity, external_reference=True, is_many=False, attribute = "root")
        serialized_head += comma + self.root.serialize(temp_etn, format = format)

        instance = self.get_instance()
        if force_external_reference:
            self.entity_structure.entry_point.external_reference = True

        if format == 'XML':
            serialized_head += "<ActualInstance>" + instance.serialize(self.entity_structure.entry_point, exported_instances = [], format = format) + "</ActualInstance>"
            serialized_tail = "</EntityInstance>"
        if format == 'JSON':
            serialized_head += ', "ActualInstance" : { ' + instance.serialize(self.entity_structure.entry_point, exported_instances = [], format = format) + " } "
            serialized_tail = " }"
        
        return serialized_head + serialized_tail



    #following methods used to be in a separate class VersionableEntityInstance

    def new_version(self, version_major=None, version_minor=None, version_patch=None, version_description = "", version_date = None):
        '''
        DATABASE: it is invoked only on default database as record go to the materialized one only
                  via the set_released method
        It creates new records for each record in the whole structure excluding extenal references
        version_released is set to False
        It creates a new EntityInstance and returns it
        
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
                instance = self.get_instance().new_version(self.entity_structure.entry_point, processed_instances = {})
                new_ei = EntityInstance()
                new_ei.version_major = version_major
                new_ei.version_minor = version_minor
                new_ei.version_patch = version_patch
                new_ei.owner_knowledge_server = KnowledgeServer.this_knowledge_server('default')
                new_ei.entity_structure = self.entity_structure
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
                    
    def set_released(self):
        '''
        Sets this version as the only released one 
        It materializes data and the EntityInstance itself
        '''
        try:
            with transaction.atomic():
                if not self.entity_structure.multiple_releases:
                    # There cannot be more than one released? I set the others to False
                    try:
                        currently_released = self.root.versions.get(version_released=True)
                        if currently_released.pk != self.pk:
                            currently_released.version_released = False
                            currently_released.save()
                        previously_released = currently_released
                    except:
                        print("EntityInstance.set_released couldn't find a released version.")
                        pass #not found
                #this one is released now
                self.version_released = True
                self.save()
                # MATERIALIZATION Now we must copy newly released self to the materialized database
                instance = self.get_instance()
                materialized_instance = instance.materialize(self.entity_structure.entry_point, processed_instances = [])
                materialized_self = self.materialize(self.shallow_entity_structure().entry_point, processed_instances = [])
                # the id should already be the same; maybe autogeneration strategies on different dbms could ... 
                materialized_self.entry_point_instance_id = materialized_instance.id
                materialized_self.save()
                if not self.entity_structure.multiple_releases:
                    # if there is only a materialized release I must set root to self otherwise deleting the previous version will delete this as well
                    materialized_self.root = materialized_self
                    materialized_self.save()
                    # now I can delete the old data set
                    if currently_released.pk != self.pk:
                        materialized_previously_released = EntityInstance.objects.using('ksm').get(URIInstance=previously_released.URIInstance)
                        materialized_previously_released.delete_entire_dataset()
               
                #end of transaction
        except Exception as e:
            print (str(e))
    
    def delete_entire_dataset(self):
        '''
        Navigating the structure deletes each record in the entire dataset obviously excluding external references
        Then it deletes self
        '''
        # TODO: add transaction
        instance = self.get_instance('ksm')
        instance.delete_children(self.entity_structure.entry_point)
        instance.delete()
        self.delete()
        
    @staticmethod
    def get_latest(any_from_the_set):
        '''
        gets the latest version starting from any EntityInstance in the version set 
        '''
        version_major__max = EntityInstance.objects.filter(root = any_from_the_set.root).aggregate(Max('version_major'))['version_major__max']
        version_minor__max = EntityInstance.objects.filter(root = any_from_the_set.root, version_major = version_major__max).aggregate(Max('version_minor'))['version_minor__max']
        version_patch__max = EntityInstance.objects.filter(root = any_from_the_set.root, version_major = version_major__max, version_minor = version_minor__max).aggregate(Max('version_patch'))['version_patch__max']
        return EntityInstance.objects.get(root = any_from_the_set, version_major = version_major__max, version_minor = version_minor__max, version_patch = version_patch__max)
   
class UploadedFile(models.Model):
    '''
    Used to save uploaded xml file so that it can be later retrieved and imported
    '''
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


# class Choices():
#     serialization_format = (        'XML', 'JSON'    ) #tuple
#     serialization_format = [        'XML', 'JSON'    ] #list

