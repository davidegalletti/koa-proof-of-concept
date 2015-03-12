# -*- coding: utf-8 -*-

from random import randrange, uniform
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.conf import settings

import kag.utils as utils
from django.db.models.manager import Manager
from django.db.models.related import RelatedObject

from xml.dom import minidom

    
class SerializableEntity(models.Model):
    
    '''
    URI_instance is the unique identifier of this SerializableEntity in this KS
    When a SerializableEntity gets imported from XML of from a remote KS a new
    URI_instance is generated using generate_URI_instance
    '''
    URI_instance = models.CharField(max_length=2000L)
    '''
    URI_imported_instance if the instance comes from XML (or a remote KS) this attribute
    stores the URI_instance as it is in the XML. Doing so I can update an instance with data
    from XML and still have a proper local URI_instance
    '''
    URI_imported_instance = models.CharField(max_length=2000L)
    
    # URI points to the a specific instance in a specific KS
    def generate_URI_instance(self, stub = False):
        if stub:
            return settings.BASE_URI + self.get_simple_entity().name_in_this_namespace
        else:
            return settings.BASE_URI + self.get_simple_entity().namespace + "/" + self.get_simple_entity().name_in_this_namespace + "/" + str(getattr(self, self.get_simple_entity().id_field))
    
    def get_simple_entity(self):
        '''
        finds the instance of class SimpleEntity where the name corresponds to the name of the class of self
        '''
        return SimpleEntity.objects.get(name=self.__class__.__name__)

    def entity_trees(self):
        '''
        Lists the entity trees associated whose entry point is the instance of class SimpleEntity corresponding to the class of self
        TODO: rinominiamo in entities ?
        '''
        return Entity.objects.filter(entry_point__simple_entity=self.get_simple_entity())

    def get_name(self):
        return getattr(self, self.get_simple_entity().name_field)
    
    def foreign_key_atributes(self): 
        attributes = []
        for key in self._meta.fields:
            if key.__class__.__name__ == "ForeignKey":
                attributes.append(key.name)
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
     
    def serialized_URIs(self, stub = False):
        return ' URISimpleEntity="' + self.get_simple_entity().URI_instance + '" '
    
    def serialized_attributes(self, stub = False):
        attributes = ""
        for key in self._meta.fields:
            if key.__class__.__name__ != "ForeignKey":
                if stub:
                    value = " generic_value "
                    if key.__class__.__name__ == "str":
                        value = "random_string"
                    if key.__class__.__name__ == "int":
                        value = str(randrange(100))
                    if key.__class__.__name__ == "long":
                        value = str(randrange(100000))
                    if key.__class__.__name__ == "float":
                        value = str(uniform(1, 10))
                    if key.__class__.__name__ == "AutoField":
                        value = "-1"
                    attributes += ' ' + key.name + '="' + value + '"'
                else:
                    attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'
        return attributes

    def to_xml(self, etn, stub = False, export_count_per_class = {}):
        str_xml = ""
        if stub:
            if not self.__class__.__name__ in  export_count_per_class.keys():
                export_count_per_class[self.__class__.__name__] = 0
            export_count_per_class[self.__class__.__name__] += 1
        if not etn.external_reference:
            if stub and export_count_per_class[self.__class__.__name__] > 3:
                return ''
            try:
                for child_node in etn.child_nodes.all():
                    print ("self." + child_node.attribute + ".__class__.__name__")
                    child_class_instance_name = child_node.simple_entity.name
                    try:
                        child_class_name = eval("self." + child_node.attribute + ".__class__.__name__")
                    except:
                        child_class_name = ""
                    child_class_module = child_node.simple_entity.module
                    if child_class_name == 'RelatedManager' or child_class_name == 'ManyRelatedManager':
                        if stub:
                            actual_class = utils.load_class(child_class_module + ".models", child_class_instance_name)
                            child_instance = actual_class()
                            # I can add a couple of children just to make it evident it is a list
                            str_xml += child_instance.to_xml(child_node, True, export_count_per_class)
                            str_xml += child_instance.to_xml(child_node, True, export_count_per_class)
                        else:
                            child_instances = eval("self." + child_node.attribute + ".all()")
                            for child_instance in child_instances:
                                # let's prevent infinite loops if self relationships
                                if (child_instance.__class__.__name__ <> self.__class__.__name__) or (self.pk <> child_node.pk):
                                    str_xml += child_instance.to_xml(child_node)
                    else:
                        if stub:
                            actual_class = utils.load_class(child_class_module + ".models", child_class_instance_name)
                            child_instance = actual_class()
                            str_xml += child_instance.to_xml (child_node, True, export_count_per_class)
                        else:
                            print "Invoking \".to_xml\" for self." + child_node.attribute
                            child_instance = eval("self." + child_node.attribute)
                            if not child_instance is None:
                                str_xml += child_instance.to_xml (child_node)
            except Exception as es:
                print es
            return '<' + self.__class__.__name__ + self.serialized_URIs(stub) + self.serialized_attributes(stub) + '>' + str_xml + '</' + self.__class__.__name__ + '>'
        else:
            # etn.external_reference = True
            xml_name = ''
            if etn.simple_entity.name_field <> "":
                if stub:
                    xml_name = " " + etn.simple_entity.name_field + "=\"Name of a sample " + etn.simple_entity.name + " instance.\""
                else:
                    xml_name = " " + etn.simple_entity.name_field + "=\"" + getattr(self, etn.simple_entity.name_field) + "\""
            if stub:
                return '<' + self.__class__.__name__ + self.serialized_URIs(True) + self._meta.pk.attname + '="-1"' + xml_name + '/>'
            else:
                return '<' + self.__class__.__name__ + self.serialized_URIs() + self._meta.pk.attname + '="' + str(self.pk) + '"' + xml_name + '/>'

    @staticmethod
    def simple_entity_from_xml_tag(self, xml_child_node):
        try:
            se = SimpleEntity.objects.get(URI_instance = xml_child_node.attributes["URISimpleEntity"].firstChild.data)
        except:
            '''
            I go get it from the appropriate KS
            TODO: David
            When I get a SimpleEntity I must generate its model in an appropriate module; the module
            name must be generated so that it is unique based on the SimpleEntity's BASE URI and on the module 
            name; 
            SimpleEntity URI 1: "http://finanze.it/KS/fattura"
            SimpleEntity URI 2: "http://finanze.it/KS/sanzione"
            
            '''
            pass
        return se

    @staticmethod
    def retrieve(actual_class, URI_instance, retrieve_externally):
        '''
        It returns an instance of a SerializableEntity stored in this KS
        It searches first on the URI_instance field (e.g. is it already an instance of this KS? ) 
        It searches then on the URI_imported_instance field (e.g. has is been imported in this KS from the same source? )
        TODO: It fetches the instance from the source as it is not in this KS yet 
        '''
        actual_instance = None
        try:
            actual_instance = actual_class.objects.get(URI_instance=URI_instance)
        except:
            try:
                actual_instance = actual_class.objects.get(URI_imported_instance=URI_instance)
            except:
                if retrieve_externally:
                    #TODO: It fetches the instance from the source as it is not in this KS yet
                    raise("To be implemented: It fetches the instance from the source as it is not in this KS yet")
                else:
                    raise("Can't find instance with URI: " + URI_instance)
            

    def from_xml(self, xmldoc, entity_node, insert=True, parent=None):
        '''
        from_xml loads from the xml an object and saves it; it searches for child nodes according
        to what the entity_node says, creates instances of child objects and call itself recursively
        Every tag corresponds to a SimpleEntity, hence it
            contains a tag <Organization> with ks_uri attribute which points to the KS managing the SimpleEntity definition
            has an attribute namespace in which SimpleEntity's name is unique;
        TODO: I would like to enforce a one-to-one correspondence between (Organization.ks_uri, namespace) and module_name
        
        Each SerializableEntity has URI_instance and URI_imported_instance attributes. 
        
        external_reference
            the first SimpleEntity in the XML cannot be marked as an external_reference in the entity_node
            from_xml doesn't get called recursively for external_references which are sought in the database
            or fetched from remote KS, so I assert self it is not an external reference
        
        '''
        field_name = ""
        if parent:
            '''
             I have a parent; let's setattr
            '''
            related_parent = getattr(parent._meta.concrete_model, entity_node.attribute)
            if related_parent.__class__.__name__ == "ForeignRelatedObjectsDescriptor":   #TODO: David comment on this
                field_name = related_parent.related.field.name
                setattr(self, field_name, parent)
            if related_parent.__class__.__name__ == "ReverseSingleRelatedObjectDescriptor":   #TODO: David comment on this
                field_name = related_parent.field.name
                setattr(self, field_name, parent)
        for key in self._meta.fields:
#              let's setattr the other attributes
            if key.__class__.__name__ != "ForeignKey" and (not parent or key.name != field_name):
                try:
                    setattr(self, key.name, xmldoc.attributes[key.name].firstChild.data)
                except:
                    print("Error extracting from xml \"" + key.name + "\" for object of class \"" + self.__class__.__name__ + "\" with ID " + str(self.id))
        try:
            # URI_imported_instance stores the URI_instance from the XML
            self.URI_imported_instance = xmldoc.attributes["URI_instance"].firstChild.data
        except:
            # there's no URI_instance in the XML; it doesn't matter
            pass
        # I must process some child nodes BEFORE SAVING self otherwise I get an error for ForeignKeys not being set
        for en_child_node in entity_node.child_nodes.all():
            if en_child_node.attribute in self.foreign_key_atributes():
                try:
                    # TODO: add assert. I assume in the XML there is exactly one child tag
                    xml_child_node = xmldoc.getElementsByTagName(en_child_node.simple_entity.name)[0] 
                    # I search for the corresponding SimpleEntity
                    
                    se = SerializableEntity.simple_entity_from_xml_tag(self, xml_child_node)
                    # TODO: I'd like the module name to be function of the organization and namespace
                    assert (en_child_node.simple_entity.name == xml_child_node.tagName == se.name), "en_child_node.simple_entity.name - xml_child_node.tagName - se.name: " + en_child_node.simple_entity.name + ' - ' + xml_child_node.tagName + ' - ' + se.name
                    module_name = en_child_node.simple_entity.module
                    actual_class = utils.load_class(module_name + ".models", xml_child_node.tagName)
                    if en_child_node.external_reference:
                        '''
                        If it is an external reference I must search for it in the database first;  
                        if it is not there I fetch it using it's URI and then create it in the database
                        '''
                        try:
                            # let's search it in the database
                            instance = SerializableEntity.retrieve(actual_class, xml_child_node.attributes["URI_instance"].firstChild.data, True)
                        except ObjectDoesNotExist:
                            # I must create it fetching it from its URI
                            pass
                        except:
                            # TODO: if it is not there I fetch it using it's URI and then create it in the database
                            raise Exception("\"" + module_name + ".models " + xml_child_node.tagName + "\" has no instance with URI_instance \"" + xml_child_node.attributes["URI_instance"].firstChild.data)
#                         # TODO: CHECK maybe next condition is better tested using concrete_model
#                         if en_child_node.attribute in self._meta.fields:
#     #                         TODO: test and add comment
#                             setattr(instance, en_child_node.attribute, self)
#                             instance.save()
#                         else:  
#     #                         TODO: test and add comment
#                             setattr(self, en_child_node.attribute, instance)
#                             self.save()
                    else:
                        if insert:
                            # the user asked to "always create", let's create the instance
                            instance = actual_class()
                        else:
                            try:
                                instance = SerializableEntity.retrieve(actual_class, xml_child_node.attributes["URI_instance"].firstChild.data, False)
                            except:
                                # didn't find it; I create the instance anyway
                                instance = actual_class()
                        # from_xml takes care of saving instance with a self.save() at the end
                        instance.from_xml(xml_child_node, en_child_node, insert) #the fourth parameter, "parent" shouldn't be necessary in this case as this is a ForeignKeys
                    setattr(self, en_child_node.attribute, instance)
                except Exception  as ex:
                    pass
                    #raise Exception("### add relevant message: from_xml")
                
        # I have added all attributes corresponding to ForeignKey, I can save it so that I can use it as a parent for the other attributes
        self.save()
        # Now I have a local ID and I can generate the URI_instance and save self again
        self.URI_instance = self.generate_URI_instance()
        self.save()

#TODO: scambiare il nesting dei loop come per le ForeignKeys
        for xml_child_node in xmldoc.childNodes:
            current_en_child_node = None
            for en_child_node in entity_node.child_nodes.all():
                if xml_child_node.tagName == en_child_node.simple_entity.name:
                    current_en_child_node = en_child_node
                    break
            # I have already processed foreign keys, I skip now
            if current_en_child_node and (not current_en_child_node.attribute in self.foreign_key_atributes()):
                # about to import the child node;
                # do I have its "URISimpleEntity" SimpleEntity in my KS?
                se = SerializableEntity.simple_entity_from_xml_tag(self, xml_child_node)
                module_name = current_en_child_node.simple_entity.module
                assert (current_en_child_node.simple_entity.name == xml_child_node.tagName == se.name), "current_en_child_node.simple_entity.name - xml_child_node.tagName - se.name: " + current_en_child_node.simple_entity.name + ' - ' + xml_child_node.tagName + ' - ' + se.name
                actual_class = utils.load_class(module_name + ".models", xml_child_node.tagName)
                if current_en_child_node.external_reference:
                    instance = SerializableEntity.retrieve(actual_class, xml_child_node.attributes["URI_instance"].firstChild.data, True)
                    # TODO: il test succesivo forse si fa meglio guardando il concrete_model
                    # TODO: capire questo test e mettere un commento
                    if current_en_child_node.attribute in self._meta.fields:
                        setattr(instance, current_en_child_node.attribute, self)
                        instance.save()
                    else:  
                        setattr(self, current_en_child_node.attribute, instance)
                        self.save()
                else:
                    if insert:
                        instance = actual_class()
                    else:
                        try:
                            instance = SerializableEntity.retrieve(actual_class, xml_child_node.attributes["URI_instance"].firstChild.data, False)
                        except:
                            instance = actual_class()
                    instance.from_xml(xml_child_node, current_en_child_node, insert, self)

    def entity_tree_stub(self, etn, export_etn, class_list=[]):
        '''
        Starting from Django ORM model we produce an Entity structure (formerly EntityTree or EntityGraph) 
        with all the relationships we find in the Django model
        '''
        module_name = self.module
        actual_class = utils.load_class(module_name + ".models", self.name)
        stub_model = actual_class()
        #vogliamo esportare l'entity come external
        sutbxmlstr = etn.to_xml(export_etn, stub=False)
        stub_xml = minidom.parseString(sutbxmlstr)
        if not actual_class in class_list:
            class_list.append(actual_class)
            fk = [f.related for f in stub_model._meta.concrete_fields if f.__class__.__name__ == "ForeignKey" or f.__class__.__name__ == "OneToOneField"]
            for rel in fk:
                actual_rel = rel.parent_model()
                #setattr(stub_model, rel.field.name, stub_model)
                #TODO: gestire meglio la presenza di .models  dentro il nome del modulo
                try:
                    rel_entity = SimpleEntity.objects.get(name=actual_rel.__class__.__name__, module=actual_rel.__class__.__module__.split(".")[0])
                except:
                    owner_organization = Organization.objects.get(pk=1) #TODO: I have to use a default organization from configuration
                    rel_entity = SimpleEntity(name=actual_rel.__class__.__name__, module=actual_rel.__class__.__module__.split(".")[0],owner_organization=owner_organization)
                    rel_entity.save()
                rel_etn = EntityNode(simple_entity=rel_entity)
                rel_xml = rel_entity.entity_tree_stub(etn=rel_etn, export_etn=export_etn, class_list=class_list)
                stub_xml.documentElement.appendChild(rel_xml.documentElement)


            for rel in stub_model._meta.get_all_related_objects():
                actual_rel = rel.model()
                setattr(actual_rel, rel.field.name, stub_model)
                #TODO: gestire meglio la presenza di .models  dentro il nome del modulo
                try:
                    rel_entity = SimpleEntity.objects.get(name=actual_rel.__class__.__name__, module=actual_rel.__class__.__module__.split(".")[0])
                except:
                    owner_organization = Organization.objects.get(pk=1) #TODO: I have to use a default organization from configuration
                    rel_entity = SimpleEntity(name=actual_rel.__class__.__name__, module=actual_rel.__class__.__module__.split(".")[0],owner_organization=owner_organization)
                    rel_entity.save()
                rel_etn = EntityNode(simple_entity=rel_entity)
                rel_xml = rel_entity.entity_tree_stub(etn=rel_etn, export_etn=export_etn, class_list=class_list)
                stub_xml.documentElement.appendChild(rel_xml.documentElement)
        return stub_xml

    class Meta:
        abstract = True

class DBConnection(models.Model):
    connection_string = models.CharField(max_length=255L)

class Workflow(SerializableEntity):
    '''
    Is a list of WorkflowMethods; the work-flow is somehow abstract, its methods do not specify details of 
    the operation but just the statuses
    '''
    name = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    entity_tree = models.ForeignKey('Entity')
#     ASSERT: I metodi di un wf devono avere impatto solo su SimpleEntity contenute nell'ET
#     ASSERT: tutte le SimpleEntity nell'ET devono ereditare da WorkflowEntityInstance
#     Un'istanza di SimpleEntity, quando viene creata, crea automaticamente un ET con solo l'SimpleEntity stessa
#     e lo associa all'istanza stessa nell'attributo: default_entity_tree
#     ASSERT: all entities must inherit from tutte le SimpleEntity devono ereditare da WorkflowEntityInstance (in cui è specificato il wf (non potrebbe essere specificato su ET
#     perché non c'è ETinstance) e lo stato corrente).

class WorkflowStatus(SerializableEntity):
    '''
    TODO: We need to have some statuses that are available to any entity and some just to specific entities; how?
    Maybe we can add a type to the statuses so that we can say that a status is of type "Initial" or "Closed"
    and the type can have some functional implications: e.g. "Closed" are not listed in a default view.
    Do we really need what's above?????? 
    '''
    name = models.CharField(max_length=100L)
    workflow = models.ForeignKey(Workflow, null=True, blank=True)
    description = models.CharField(max_length=2000L, blank=True)

class WorkflowEntityInstance(SerializableEntity):
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

class Organization(SerializableEntity):
    name = models.CharField(max_length=500L, blank=True)
    description = models.CharField(max_length=2000L, blank=True)
    ks_uri = models.CharField(max_length=500L, blank=True)

class SimpleEntity(SerializableEntity):
    '''
    Every entity has a work-flow; the basic one is the one that allows a method to create an instance
    '''
    owner_organization = models.ForeignKey(Organization)
    # the namespace from the organization owner of this SimpleEntity 
    namespace = models.CharField(max_length=500L, blank=True)
    name_in_this_namespace = models.CharField(max_length=500L, blank=True)
    
    # name corresponds to the class name
    name = models.CharField(max_length=100L)
    # for Django it corresponds to the module which contains the class 
    module = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    table_name = models.CharField(max_length=255L, db_column='tableName', blank=True)
    id_field = models.CharField(max_length=255L, db_column='idField', blank=True)
    name_field = models.CharField(max_length=255L, db_column='nameField', blank=True)
    description_field = models.CharField(max_length=255L, db_column='descriptionField', blank=True)
    connection = models.ForeignKey(DBConnection, null=True, blank=True)

    # URI points to the KS that manages SimpleEntity's metadata
    # e.g. http://finanze.it/KS/fattura
    def URI(self):
        return self.owner_organization.ks_uri + "/" + self.namespace + "/" + self.name

class AttributeType(SerializableEntity):
    name = models.CharField(max_length=255L, blank=True)
    widgets = models.ManyToManyField('application.Widget', blank=True)

class Attribute(SerializableEntity):
    name = models.CharField(max_length=255L, blank=True)
    simple_entity = models.ForeignKey('SimpleEntity', null=True, blank=True)
    type = models.ForeignKey('AttributeType')
    def __str__(self):
        return self.entity.name + "." + self.name

class EntityNode(SerializableEntity):
    simple_entity = models.ForeignKey('SimpleEntity')
    # attribute is blank for the entry point
    attribute = models.CharField(max_length=255L, blank=True)
    child_nodes = models.ManyToManyField('self', blank=True, symmetrical=False)
    # if not external_reference all attributes are exported, otherwise only the id
    external_reference = models.BooleanField(default=False, db_column='externalReference')

class Entity(SerializableEntity):
    '''
    It is a graph that defines a set of entities on which we can perform a task; the tree has
    an entry point which is a Node e.g. an entity; from an instance of an entity we can use
    the "attribute" attribute from the corresponding EntityNode to get the instances of
    the entities related to each of the child_nodes. An Entity could, for example, tell
    us what to export to xml/json, what to consider as a "VersionableMultiEntity" (e.g. an
    instance of VersionableEntityInstance + an Entity where the entry_point points to that instance)
    The name should describe its use
    '''
    name = models.CharField(max_length=200L)
    description = models.CharField(max_length=2000L)
    entry_point = models.ForeignKey('EntityNode')

class EntityInstance(SerializableEntity):
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
    
    entity_tree = models.ForeignKey(Entity)
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
