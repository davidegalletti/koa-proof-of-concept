# -*- coding: utf-8 -*-
from django.db import models

import kag.utils as utils
from django.db.models.manager import Manager
from django.db.models.related import RelatedObject



class SerializableEntity(models.Model):
    
    def entity_instance(self):
        '''
        finds the instance of class Entity where the name corresponds to the name of the class of self
        '''
        return Entity.objects.get(name=self.__class__.__name__)

    def entity_trees(self):
        '''
        Lists the entity trees associated whose entry point is the instance of class Entity corresponding to the class of self
        '''
        return EntityTree.objects.filter(entry_point__entity=self.entity_instance())

    def get_name(self):
        return getattr(self, self.entity_instance().name_field)
    
    def foreign_key_atributes(self): 
        attributes = ""
        for key in self._meta.fields:
            if key.__class__.__name__ == "ForeignKey":
                attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'
        return attributes
                
    def related_manager_atributes(self): 
        attributes = ""
        for key in self._meta.fields:
            if key.__class__.__name__ == "RelatedManager":
                attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'
        return attributes
                
    def many_related_manager_atributes(self): 
        attributes = ""
        for key in self._meta.fields:
            if key.__class__.__name__ == "ManyRelatedManager":
                attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'
        return attributes
            
    def serialized_attributes(self):
        attributes = ""
        for key in self._meta.fields:
            if key.__class__.__name__ != "ForeignKey":
                attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'
        return attributes

    def to_xml(self, etn):
        str_xml = ""
        if not etn.external_reference:
            for child_node in etn.child_nodes.all():
                print ("self." + child_node.attribute + ".__class__.__name__")
                child_class_name = eval("self." + child_node.attribute + ".__class__.__name__")
                if child_class_name == 'RelatedManager' or child_class_name == 'ManyRelatedManager':
                    child_instances = eval("self." + child_node.attribute + ".all()")
                    for child_instance in child_instances:
                        # let's prevent infinite loops if self relationships
                        if (child_instance.__class__.__name__ <> self.__class__.__name__) or (self.pk <> child_node.pk):
                            str_xml += child_instance.to_xml(child_node)
                else:
                    print "Invoking \".to_xml\" for self." + child_node.attribute
                    child_instance = eval("self." + child_node.attribute)
                    if not child_instance is None:
                        str_xml += child_instance.to_xml (child_node)
            return '<' + self.__class__.__name__ + ' ' + self.serialized_attributes() + '>' + str_xml + '</' + self.__class__.__name__ + '>'
        else:
            if etn.entity.name_field <> "":
                xml_name = " " + etn.entity.name_field + "=\"" + getattr(self, etn.entity.name_field) + "\""
            return '<' + self.__class__.__name__ + ' ' + self._meta.pk.attname + '="' + str(self.pk) + '"' + xml_name + '/>'

    def from_xml(self, xmldoc, etn, insert=True, parent=None):
        if not etn.external_reference:
            field_name = ""
            if parent:
                related_parent = getattr(parent._meta.concrete_model, etn.attribute)
                if related_parent.__class__.__name__ == "ForeignRelatedObjectsDescriptor":
                    field_name = related_parent.related.field.name
                    setattr(self, field_name, parent)
                if related_parent.__class__.__name__ == "ReverseSingleRelatedObjectDescriptor":
                    field_name = related_parent.field.name
                    setattr(self, field_name, parent)
            for key in self._meta.fields:
                if key.__class__.__name__ != "ForeignKey" and (not parent or key.name != field_name):
                    try:
                        setattr(self, key.name, xmldoc.attributes[key.name].firstChild.data)
                    except:
                        print("Error extracting from xml \"" + key.name + "\" for object of class \"" + self.__class__.__name__ + "\" with ID " + str(self.id))
        self.save()
        
        for xml_child_node in xmldoc.childNodes:
            current_etn_child_node = None
            for etn_child_node in etn.child_nodes.all():
                if xml_child_node.tagName == etn_child_node.entity.name:
                    current_etn_child_node = etn_child_node
                    break
            if current_etn_child_node:
                module_name = current_etn_child_node.entity.module
                actual_class = utils.load_class(module_name + ".models", xml_child_node.tagName)
                if not current_etn_child_node.external_reference:
                    if insert:
                        instance = actual_class()
                    else:
                        instance = actual_class.objects.get(pk=xml_child_node.attributes[actual_class._meta.pk.attname].firstChild.data)
                    instance.from_xml(xml_child_node, current_etn_child_node, insert, self)
                else:
                    instance = actual_class.objects.get(pk=xml_child_node.attributes[actual_class._meta.pk.attname].firstChild.data)
                    # TODO: il test succesivo forse si fa meglio guardando il concrete_model
                    if current_etn_child_node.attribute in self._meta.fields:
#                         TODO: test
                        setattr(instance, current_etn_child_node.attribute, self)
                        instance.save()
                    else:  
#                         TODO: test
                        setattr(self, current_etn_child_node.attribute, instance)
                        self.save()
    class Meta:
        abstract = True




class DBConnection(models.Model):
    connection_string = models.CharField(max_length=255L)

# class WorkflowEntity(SerializableEntity):
#     '''
#     WorkflowEntity is a generic entity with a work-flow status; such a status is used also for minimal work-flow of entities that are either in "working" or "released" status
#     '''

class Workflow(SerializableEntity):
    '''
    Is a list of WorkflowMethods; the work-flow is somehow abstract, its methods do not specify details of 
    the operation but just the statuses
    '''
    name = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    entity_tree = models.ForeignKey('EntityTree')
#     ASSERT: I metodi di un wf devono avere impatto solo su Entity contenute nell'ET
#     ASSERT: tutte le Entity nell'ET devono ereditare da WorkflowEntityInstance
#     Un'istanza di Entity, quando viene creata, crea automaticamente un ET con solo l'Entity stessa
#     e lo associa all'istanza stessa nell'attributo: default_entity_tree
#     ASSERT: all entities must inherit from tutte le Entity devono ereditare da WorkflowEntityInstance (in cui è specificato il wf (non potrebbe essere specificato su ET
#     perché non c'è ETinstance) e lo stato corrente).

class WorkflowStatus(SerializableEntity):
    '''
    TODO: We need to have some statuses that are available to any entity and some just to specific entities; how?
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


class WorkflowMethod(SerializableEntity):
    '''
    If there are no initial_statuses then this is a method which creates the entity
    TODO: Can the final status be dynamically determined by the implementation?
    '''
    initial_statuses = models.ManyToManyField(WorkflowStatus, blank=True, related_name="+")
    final_status = models.ForeignKey(WorkflowStatus, related_name="+")
    workflow = models.ForeignKey(Workflow)

    class Meta:
        abstract = True

class WorkflowTransition():
    instance = models.ForeignKey(WorkflowEntityInstance)
    workflow_method = models.ForeignKey('WorkflowMethod')
    notes = models.TextField()
    user = models.ForeignKey('userauthorization.KUser')
    timestamp = models.DateTimeField(auto_now_add=True)
    status_from = models.ForeignKey(WorkflowStatus, related_name="+")


class Entity(SerializableEntity):
    '''
    Every entity has a work-flow; the basic one is the one that allows a method to create an instance
    '''
    URI = models.CharField(max_length=400L, blank=True)
    # corresponds to the class name
    name = models.CharField(max_length=100L)
    # for Django it corresponds to the module which contains the class 
    module = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    table_name = models.CharField(max_length=255L, db_column='tableName', blank=True)
    id_field = models.CharField(max_length=255L, db_column='idField', blank=True)
    name_field = models.CharField(max_length=255L, db_column='nameField', blank=True)
    description_field = models.CharField(max_length=255L, db_column='descriptionField', blank=True)
    connection = models.ForeignKey(DBConnection, null=True, blank=True)

class AttributeType(SerializableEntity):
    name = models.CharField(max_length=255L, blank=True)
    widgets = models.ManyToManyField('application.Widget', blank=True)

class Attribute(SerializableEntity):
    name = models.CharField(max_length=255L, blank=True)
    entity = models.ForeignKey('Entity', null=True, blank=True)
    type = models.ForeignKey('AttributeType')
    def __str__(self):
        return self.entity.name + "." + self.name

class EntityTreeNode(SerializableEntity):
    entity = models.ForeignKey('Entity')
    # attribute is blank for the entry point
    attribute = models.CharField(max_length=255L, blank=True)
    child_nodes = models.ManyToManyField('self', blank=True, symmetrical=False)
    # if not external_reference all attributes are exported, otherwise only the id
    external_reference = models.BooleanField(default=False, db_column='externalReference')

class EntityTree(SerializableEntity):
    '''
    It is a tree that defines a set of entities on which we can perform a task; the tree has
    an entry point which is a Node e.g. an entity; from an instance of an entity we can use
    the "attribute" attribute from the corresponding EntityTreeNode to get the instances of
    the entities related to each of the child_nodes. An EntityTree could, for example, tell
    us what to export to xml/json, what to consider as a "VersionableMultiEntity" (e.g. an
    instance of VersionableEntityInstance + an EntityTree where the entry_point points to that instance)
    The name should describe its use
    '''
    URI = models.CharField(max_length=400L, blank=True)
    name = models.CharField(max_length=200L)
    entry_point = models.ForeignKey('EntityTreeNode')

class EntityTreeInstance(SerializableEntity):
    '''
    Versionable
    an Instance belongs to a set of instances which are basically the same but with a different version
    
    Methods:
        new version: create new instances starting from entry point, following the nodes but those with external_reference=True
        release: it sets version_released True and it sets it to False for all the other instances of the same set
    '''
    
    '''
    an Instance belongs to a set of instances which are basically the same but with a different version
    root_version_id is the id of the first instance of this set 
    '''
    root_version_id = models.IntegerField()
    
    entity_tree = models.ForeignKey(EntityTree)
    entry_point_id = models.IntegerField()
    version_major = models.IntegerField(blank=True)
    version_minor = models.IntegerField(blank=True)
    version_patch = models.IntegerField(blank=True)
    '''
    At most one instance with the same root_version_id has version_released = True
    Three states: working, released, obsolete
    working is the latest version where version_released = False
    released is the one with version_released = True
    obsolete are the others 
    '''
    version_released = models.BooleanField(default=False)
    
    
    
    

class UploadedFile(models.Model):
    '''
    Used to save uploaded xml file so that it can be later retrieved and imported
    '''
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
