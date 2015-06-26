# -*- coding: utf-8 -*-

from datetime import datetime

from random import randrange, uniform
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Max

from django.conf import settings
from userauthorization.models import KUser
import kag.utils as utils

from xml.dom import minidom

    
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
        try:
            return settings.THIS_KS_URI + self.get_simple_entity().namespace + "/" + self.get_simple_entity().name_in_this_namespace + "/" + str(getattr(self, self.get_simple_entity().id_field))
        except:
            return ""
    
    def get_simple_entity(self, class_name = ""):
        '''
        finds the instance of class SimpleEntity where the name corresponds to the name of the class of self
        '''
        if class_name == "":
            return SimpleEntity.objects.get(name=self.__class__.__name__)
        else:
            return SimpleEntity.objects.get(name=class_name)

    def entities(self):
        '''
        Lists the entities associated whose entry point is the instance of class SimpleEntity corresponding to the class of self
        '''
        return Entity.objects.filter(entry_point__simple_entity=self.get_simple_entity())

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
        for key in self._meta.fields:
            if key.__class__.__name__ != "ForeignKey":
                if format == 'XML':
                    attributes += ' ' + key.name + '="' + str(getattr(self, key.name)) + '"'  
                if format == 'JSON':
                    attributes += '"' + key.name + '" : "' + str(getattr(self, key.name)) + '", '
        return attributes

    def shallow_entity(self):
        '''
        if a user wants to serialize a SerializableSimpleEntity without passing an Entity
        I search for an Entity with shallow=True; if I can't find it I create it and save it
        for future use
        '''
        try:
            se = Entity.objects.get(entry_point__simple_entity = self.get_simple_entity(), shallow = True)
        except:
            se = Entity()
            se.shallow = True
            se.name = self.__class__.__name__ + " (shallow)"
            se.simple_entity = self.get_simple_entity()
            se.entry_point = self.shallow_entity_node()
            se.save()
            se.URIInstance = se.generate_URIInstance()
            se.save()
        return se 
        
    def shallow_entity_node(self):
        '''
        it creates an EntityNode used to serialize (to_xml) self. It has the SimpleEntity 
        and references to ForeignKeys and ManyToMany
        '''
        etn = EntityNode()
        etn.simple_entity = self.get_simple_entity() 
        etn.external_reference=False
        etn.is_many=False
        etn.save()
        etn.child_nodes = []
        for fk in self.foreign_key_attributes():
            etn_fk = EntityNode()
            if getattr(self, fk) is None:
                # the attribute is not set so I can't get its __class__.__name__ and I take it from the model
                class_name = self._meta.get_field('entity').rel.model.__name__
                etn_fk.simple_entity = self.get_simple_entity(class_name)
            else:
                etn_fk.simple_entity = getattr(self, fk).get_simple_entity()
            etn_fk.external_reference=True
            etn_fk.attribute = fk
            etn_fk.is_many=False
            etn_fk.save()
            etn.child_nodes.add(etn_fk)
        for rm in self.related_manager_attributes():
            #TODO: shallow_entity_node: implement self.related_manager_attributes case
            pass
        for mrm in self.many_related_manager_attributes():
            #TODO: shallow_entity_node: implement self.many_related_manager_attributes case
            pass
        etn.save()
        return etn

    def serialize(self, etn = None, export_count_per_class = {}, exported_instances = [], format = 'XML'):
        '''
        format: {'XML' | 'JSON'}
        '''
        format = format.upper()
        serialized = ""
        '''
            If I have already exported this instance I don't want to duplicate all details hence I just export it's URIInstance, 
            name and SimpleEntity URI. Then I need to add an attribute so that when importing it I will recognize that its details
            are somewhere else in the file
            <EntityNode URISimpleEntity="....." URIInstance="...." attribute="...." KS_TAG_WITH_NO_DATA=""
            the TAG "KS_TAG_WITH_NO_DATA" is used to mark the fact that the details of this entity are somewhereelse in the file
        '''
        # if there is no etn I export just this object creating a shallow Entity 
        if etn is None:
            etn = self.shallow_entity().entry_point
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
                for child_node in etn.child_nodes.all():
                    if child_node.is_many:
                        child_instances = eval("self." + child_node.attribute + ".all()")
                        if format == 'XML':
                            serialized += "<" + child_node.attribute + ">"
                        if format == 'JSON':
                            serialized += '"' + child_node.attribute + '" : ['
                        comma = ""
                        for child_instance in child_instances:
                            # let's prevent infinite loops if self relationships
                            if (child_instance.__class__.__name__ != self.__class__.__name__) or (self.pk != child_node.pk):
                                if format == 'JSON':
                                    serialized += comma
                                serialized += child_instance.serialize(child_node, exported_instances=exported_instances, format=format)
                            comma = ", "
                        if format == 'XML':
                            serialized += "</" + child_node.attribute + ">"
                        if format == 'JSON':
                            serialized += "]"
                    else:
                        child_instance = eval("self." + child_node.attribute)
                        if not child_instance is None:
                            serialized += child_instance.serialize(child_node, format=format, exported_instances=exported_instances)
            except Exception as es:
                print es
            if format == 'XML':
                return '<' + tag_name + self.serialized_URI_SE(format) + self.serialized_attributes(format) + '>' + serialized + '</' + tag_name + '>'
            if format == 'JSON':
                if etn.is_many:
                    return ' { ' + self.serialized_URI_SE(format) + ', ' + self.serialized_attributes(format) + serialized + ' }'
                else:
                    return '"' + tag_name + '" : { ' + self.serialized_URI_SE(format) + ', ' + self.serialized_attributes(format) + serialized + ' }'
            
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
            
            '''
            #estrarre l'url del KS
            ks_url = ""
            #encode di URIInstance
            URIInstance_base64 = ""
            #wget ks_url + "/ks/api/simple_entity_definition/" + URIInstance_base64
            raise Exception("TO BE IMPLEMENTED in simple_entity_from_xml_tag: get SimpleEntity from appropriate KS.")
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
                    raise Exception("To be implemented: It fetches the instance from the source as it is not in this KS yet")
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
        
    def from_xml(self, xmldoc, entity_node, insert=True, parent=None):
        '''
        from_xml gets from xmldoc the attributes of self and saves it; it searches for child nodes according
        to what the entity_node says, creates instances of child objects and call itself recursively
        Every tag corresponds to a SimpleEntity, hence it
            contains a tag URISimpleEntity which points to the KS managing the SimpleEntity definition
        
        Each SerializableSimpleEntity has URIInstance and URI_imported_instance attributes. 
        
        external_reference
            the first SimpleEntity in the XML cannot be marked as an external_reference in the entity_node
            from_xml doesn't get called recursively for external_references which are sought in the database
            or fetched from remote KS, so I assert self it is not an external reference
        
        '''
        field_name = ""
        if parent:
#           I have a parent; let's set it
            field_name = SerializableSimpleEntity.get_parent_field_name(parent, entity_node.attribute)
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
            module_name = entity_node.simple_entity.module
            actual_class = utils.load_class(module_name + ".models", entity_node.simple_entity.name) 
            try:
                instance = SerializableSimpleEntity.retrieve(actual_class, xmldoc.attributes["URIInstance"].firstChild.data, False)
                # It's in the database; I just need to set its parent; data is either already there or it will be updated later on
                if parent:
                    field_name = SerializableSimpleEntity.get_parent_field_name(parent, entity_node.attribute)
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
#              let's setattr the other attributes
#                that are not ForeignKey as those are treated separately
#                and is not the field_name pointing at the parent as it has been already set
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
        for en_child_node in entity_node.child_nodes.all():
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
                        instance.from_xml(xml_child_node, en_child_node, insert) #the fourth parameter, "parent" shouldn't be necessary in this case as this is a ForeignKeys
                    setattr(self, en_child_node.attribute, instance)
                except Exception as ex:
                    print (ex.message)
                    pass
                    #raise Exception("### add relevant message: from_xml")
                 
        # I have added all attributes corresponding to ForeignKey, I can save it so that I can use it as a parent for the other attributes
        self.save()
        # from_xml can be invoked on an instance retrieved from the database (where URIInstance is set)
        # or created on the fly (and URIInstance is not set); in the latter case, only now I can generate URIInstance
        # as I have just saved it and I have a local ID
        if not self.URIInstance:
            self.URIInstance = self.generate_URIInstance()
            self.save()
 
        for en_child_node in entity_node.child_nodes.all():
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

class Workflow(SerializableSimpleEntity):
    '''
    Is a list of WorkflowMethods; the work-flow is somehow abstract, its methods do not specify details of 
    the operation but just the statuses
    '''
    name = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    entity = models.ForeignKey('Entity', null = True, blank=True)
#     ASSERT: I metodi di un wf devono avere impatto solo su SimpleEntity contenute nell'Entity

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


class WorkflowMethod(SerializableSimpleEntity):
    '''
    If there are no initial_statuses then this is a method which creates the entity
    '''
    initial_statuses = models.ManyToManyField(WorkflowStatus, blank=True, related_name="+")
    final_status = models.ForeignKey(WorkflowStatus, related_name="+")
    workflow = models.ForeignKey(Workflow)

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

class KnowledgeServer(SerializableSimpleEntity):
    name = models.CharField(max_length=500L, blank=True)
    description = models.CharField(max_length=2000L, blank=True)
    # ASSERT: only one KnowledgeServer in each KS has this_ks = True; I use it to know in which KS I am
    this_ks = models.BooleanField(default=False)
    uri = models.CharField(max_length=500L, blank=True)
    organization = models.ForeignKey(Organization)

class SimpleEntity(SerializableSimpleEntity):
    '''
    Every entity has a work-flow; the basic one is the one that allows a method to create an instance
    '''
    name_in_this_namespace = models.CharField(max_length=500L, blank=True)
    
    # this name corresponds to the class name
    name = models.CharField(max_length=100L)
    # for Django it corresponds to the module which contains the class 
    module = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    table_name = models.CharField(max_length=255L, db_column='tableName', blank=True)
    id_field = models.CharField(max_length=255L, db_column='idField', blank=True)
    name_field = models.CharField(max_length=255L, db_column='nameField', blank=True)
    description_field = models.CharField(max_length=255L, db_column='descriptionField', blank=True)
    connection = models.ForeignKey(DBConnection, null=True, blank=True)

class AttributeType(SerializableSimpleEntity):
    name = models.CharField(max_length=255L, blank=True)
    widgets = models.ManyToManyField('application.Widget', blank=True)

class Attribute(SerializableSimpleEntity):
    name = models.CharField(max_length=255L, blank=True)
    simple_entity = models.ForeignKey('SimpleEntity', null=True, blank=True)
    type = models.ForeignKey('AttributeType')
    def __str__(self):
        return self.simple_entity.name + "." + self.name

class EntityNode(SerializableSimpleEntity):
    simple_entity = models.ForeignKey('SimpleEntity')
    # attribute is blank for the entry point
    attribute = models.CharField(max_length=255L, blank=True)
    # related_name "parent_entity_node" is not used now
    child_nodes = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="parent_entity_node")
    # if not external_reference all attributes are exported, otherwise only the id
    external_reference = models.BooleanField(default=False, db_column='externalReference')
    # is_many is true if the attribute correspond to a list of instances of the SimpleEntity
    is_many = models.BooleanField(default=False, db_column='isMany')

class Entity(SerializableSimpleEntity):
    '''
    Main idea behind the model: an entity is not represented by a single class or a single 
    table in a database but it is usually represented using a collection of them: more than 
    one class and more than one table in the database. An Issue in a tracking system is an 
    entity; it has a list of notes that can be appended to it, it has a user who has created
    it, and many other attributes. The user does not belong just to this entity, hence it
    is a reference; the notes do belong to the issue. The idea is to map the set of tables
    in a (relational) database into entities so that our operations can handle this more
    generic entity that we are defining, composed with more than one simple entity (in 
    more direct correspondence with a database table, SimpleEntity in our model). A simple
    entity can be in more than one entity; because, for instance, we might like to render/...
    .../export/... a subset of the simple entities of a complex entity.
    When we get to EntityInstance (which inherits from VersionableEntityInstance and 
    WorkflowEntityInstance) we must add a constraint because we want a unique way
    to know the version and the status of a simple instance: take the set of entities
    in the entity attribute of all instances of EntityInstance. In the graph of each
    entity, consider only the simple entities that are not references; the constraint
    is that each simple entity must not be in the graph of more than one entity; otherwise
    it would be impossible to determine its version and status. In other words the entities
    used by EntityInstance must partition the E/R diagram of our database in graphs without
    any intersection. 
     
    
    An Entity is a graph that defines a set of simple entities on which we can perform a task; 
    it has an entry point which is a Node e.g. an entity; from an instance of an entity we can use
    the "attribute" attribute from the corresponding EntityNode to get the instances of
    the entities related to each of the child_nodes. An Entity could, for example, tell
    us what to export to xml/json, ???????????????? what to consider as a "VersionableMultiEntity" (e.g. an
    instance of VersionableEntityInstance + an Entity where the entry_point points to that instance)
    The name should describe its use ?????????????????
    '''
    name = models.CharField(max_length=200L)
    description = models.CharField(max_length=2000L)
    '''
    an Entity is shallow when it is automatically created to export a SimpleEntity; 
    shallow means that all foreignKeys and related attributes are external references
    '''
    shallow = models.BooleanField(default=False)
    entry_point = models.ForeignKey('EntityNode')

class VersionableEntityInstance(models.Model):
    '''
    Versionable
    an Instance belongs to a set of instances which are basically the same but with a different version
    
    Methods:
        new version: create new instances starting from entry point, following the nodes but those with external_reference=True
        release: it sets version_released True and it sets it to False for all the other instances of the same set
    '''
    
    '''
    an Instance belongs to a set of instances which are basically the same but with a different version
    root is the first instance of this set; root has root=self so that if I filter for root=smthng
    I get all of them including the root
    WE REFER TO SUCH SET AS THE "version set"
    '''
    root = models.ForeignKey('self', related_name='versions')
    # http://semver.org/
    version_major = models.IntegerField(blank=True)
    version_minor = models.IntegerField(blank=True)
    version_patch = models.IntegerField(blank=True)
    version_description = models.CharField(max_length=2000L, default = "")
    '''
    Assert: At most one instance with the same root_version_id has version_released = True
    '''
    version_released = models.BooleanField(default=False)

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
    
    @staticmethod
    def get_latest(any_from_the_set):
        '''
        gets the latest version starting from any EntityInstance in the version set 
        '''
        version_major__max = EntityInstance.objects.filter(root = any_from_the_set.root).aggregate(Max('version_major'))['version_major__max']
        version_minor__max = EntityInstance.objects.filter(root = any_from_the_set.root, version_major = version_major__max).aggregate(Max('version_minor'))['version_minor__max']
        version_patch__max = EntityInstance.objects.filter(root = any_from_the_set.root, version_major = version_major__max, version_minor = version_minor__max).aggregate(Max('version_patch'))['version_patch__max']
        return EntityInstance.objects.get(root = any_from_the_set, version_major = version_major__max, version_minor = version_minor__max, version_patch = version_patch__max)
    
    class Meta:
        abstract = True
    
class EntityInstance(WorkflowEntityInstance, VersionableEntityInstance, SerializableSimpleEntity):
    '''
    A chunk of knowledge; its data structure is described by self.entity
    The only Versionable object so far
    Serializable like many others 
    It has an owner KS which can be inferred by the URIInstance but it is explicitly linked 
    '''
    owner_knowledge_server = models.ForeignKey(KnowledgeServer)
    # NOT USED YET; the namespace from the organization owner of this EntityInstance 
    namespace = models.CharField(max_length=500L, blank=True)

    entity = models.ForeignKey(Entity)
    # we have the ID of the instance because we do not know its class so we can't have a ForeignKey to an unknown class
    entry_point_instance_id = models.IntegerField()

    def serialize_with_simple_entity(self, format = 'XML', force_external_reference=False):
        format = format.upper()
        if format == 'XML':
            serialized_head = "<EntityInstance EntryPointInstanceId=\"" + str(self.entry_point_instance_id) + "\" InstanceURI=\"" + self.URIInstance + "\" VersionMajor=\"" + str(self.version_major) + "\" VersionMinor=\"" + str(self.version_minor) + "\" VersionPatch=\"" + str(self.version_patch) + "\" VersionReleased=\"" + str(self.version_released) + "\" VersionDescription=\"" + self.version_description + "\">"
        if format == 'JSON':
            serialized_head = ' { "EntryPointInstanceId" : "' + str(self.entry_point_instance_id) + '", "InstanceURI" : "' + self.URIInstance + '", "VersionMajor" : "' + str(self.version_major) + '", "VersionMinor" : "' + str(self.version_minor) + '", "VersionPatch" : "' + str(self.version_patch) + '", "VersionReleased" : "' + str(self.version_released) + '", "VersionDescription" : "' + self.version_description + '" '
        comma = ""    
        if format == 'JSON':
            comma = ", "
        e_simple_entity = SimpleEntity.objects.get(name="Entity")
        temp_etn = EntityNode(simple_entity=e_simple_entity, external_reference=True, is_many=False, attribute = "")
        if format == 'XML':
            serialized_head += comma + self.entity.serialize(temp_etn, format = format)
        if format == 'JSON':
            serialized_head += comma + self.entity.serialize(temp_etn, format = format)
        
        ei_simple_entity = SimpleEntity.objects.get(name="EntityInstance")
        temp_etn = EntityNode(simple_entity=ei_simple_entity, external_reference=True, is_many=False, attribute = "root")
        if format == 'XML':
            serialized_head += comma + self.root.serialize(temp_etn, format = format)
        if format == 'JSON':
            serialized_head += comma + self.root.serialize(temp_etn, format = format)

        w_simple_entity = SimpleEntity.objects.get(name="Workflow")
        temp_etn = EntityNode(simple_entity=w_simple_entity, external_reference=True, is_many=False, attribute = "")
        if format == 'XML':
            serialized_head += comma + self.workflow.serialize(temp_etn, format = format)
        if format == 'JSON':
            serialized_head += comma + self.workflow.serialize(temp_etn, format = format)
        
        ws_simple_entity = SimpleEntity.objects.get(name="WorkflowStatus")
        temp_etn = EntityNode(simple_entity=ws_simple_entity, external_reference=True, is_many=False, attribute = "current_status")
        if format == 'XML':
            serialized_head += comma + self.current_status.serialize(temp_etn, format = format)
        if format == 'JSON':
            serialized_head += comma + self.current_status.serialize(temp_etn, format = format)
        
        se_simple_entity = self.entity.entry_point.simple_entity
        actual_class = utils.load_class(se_simple_entity.module + ".models", se_simple_entity.name)
        instance = actual_class.objects.get(pk=self.entry_point_instance_id)
        if force_external_reference:
            self.entity.entry_point.external_reference = True

        if format == 'XML':
            serialized_head += "<ActualInstance>" + instance.serialize(self.entity.entry_point, exported_instances = [], format = format) + "</ActualInstance>"
            serialized_tail = "</EntityInstance>"
        if format == 'JSON':
            serialized_head += ', "ActualInstance" : { ' + instance.serialize(self.entity.entry_point, exported_instances = [], format = format) + " } "
            serialized_tail = " }"
        
        return serialized_head + serialized_tail


#     def initialize(self, version_major=0, version_minor=1, version_patch=0):
#         '''
#         ???It was a __init__ not 100% clear apart from initializing a version and a entry_point_instance_id???
#         '''
#         actual_class = utils.load_class(self.entity.entry_point.simple_entity.module + ".models", self.entity.entry_point.simple_entity.name)
#         entry_point_instance = actual_class()
#         entry_point_instance.SetNotNullFields()
#         entry_point_instance.save()
#         self.entry_point_instance_id = entry_point_instance.id

#     def get_version_released(self, released = False, latest = False, version_major=None, version_minor=None, version_patch=None):
#         '''
#         version-aware proxy to objects.get 
#         '''
#         if released:
#             pass
#     
#     def filter_version_released(self):
#         '''
#         version-aware proxy to objects.filter 
#         '''
#         pass
   
class UploadedFile(models.Model):
    '''
    Used to save uploaded xml file so that it can be later retrieved and imported
    '''
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')


# class Choices():
#     serialization_format = (        'XML', 'JSON'    ) #tuple
#     serialization_format = [        'XML', 'JSON'    ] #list
