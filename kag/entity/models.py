from django.db import models


class DBConnection(models.Model):
    connection_string = models.CharField(max_length=255L)



class WorkflowEntity(models.Model):
    '''
    Abstract class
    WorkflowEntity is a generic entity with a work-flow status; such a status is used also for minimal work-flow of entities that are either in "working" or "released" status
    '''
    workflow = models.ForeignKey('Workflow', null=True, blank=True, related_name = "+")
    class Meta:
        abstract = True
    
class Workflow(WorkflowEntity):
    '''
    Is a list of WorkflowMethods; the work-flow is abstract, its methods do not specify details of the operation but just the statuses
    '''
    name = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
  
class WorkflowStatus(models.Model):
    '''
    TODO: We need to have some statuses that are available to any entity and some just to specific entities; how?
    '''
    name = models.CharField(max_length=100L)
    workflow = models.ForeignKey(Workflow, null=True, blank=True)
    description = models.CharField(max_length=2000L, blank=True)


class WorkflowEntityInstance(models.Model):
    '''
    Abstract class
    WorkflowEntityInstance
    '''
    current_status = models.ForeignKey(WorkflowStatus)
    class Meta:
        abstract = True
    
    
class VersionableEntityInstance(models.Model):
    '''
    Abstract class
    VersionableEntityInstance is ....
    '''
    version = models.IntegerField(blank=True)
    class Meta:
        abstract = True
    
class WorkflowMethod(models.Model):
    '''
    If there are no initial_statuses then this is a method which creates the entity
    TODO: Can the final status be dynamically determined by the implementation?
    '''
    initial_statuses = models.ManyToManyField(WorkflowStatus, blank=True, related_name="+")
    final_status = models.ForeignKey(WorkflowStatus, related_name="+")
    workflow = models.ForeignKey(Workflow)

    class Meta:
        abstract = True

class genericEntity():
    
    def entity_instance(self):
        '''
        finds the instance of class Entity where the name corresponds to the name of the class of self
        '''
        return Entity.objects.get(name=self.__class__.__name__)
    
    def entity_trees(self):
        '''
        Lists the entity trees associated whose entry point is the instance of class Entity corresponding to the class of self
        '''
        return EntityTree.objects.filter(entry_point__entity = self.entity_instance)
    

class SerializableEntity(genericEntity):
    def serializable_attributes(self):
        """
        TODO: use the class name instead of the syntax (e.g. _id, _set) to remove foreign keys 
        lists all the attributes that can be serialized and 
        their values excluding "pk" and those: 
         - starting and ending with "_"
         - starting with "_"
         - ending with "_set"
         - ending with "_id" and "*" where "*_id"
         ManyRelatedManager
         RelatedManager
        """
        out = {}
        fk = []
        for names in dir(self):
            if names[-3:] == "_id":
                fk.append(names[:-3])
                fk.append(names)
        for names in dir(self):
            if names<>"objects":
                attr = getattr(self,names)
                if (not callable(attr)) and names[:1] <> "_" and (not (names[:1] == "_" and names[-1:] == "_")) and names[-4:] <> "_set" and (not names in fk) and names <> 'pk' and (not (eval("self." + names + ".__class__.__name__") in ['ManyRelatedManager', 'RelatedManager'] )):
                    out[names] = str(attr)
        return out
    def serialized_attributes(self):
        attributes = ""
        for key, value in self.serializable_attributes().iteritems():
            attributes += ' ' + key + '="' + value + '"'
        return attributes
    def to_xml(self, etn):
        str_xml = ""
        for child_node in etn.child_nodes.all():
            if eval("self." + child_node.attribute + ".__class__.__name__") == 'RelatedManager':
                child_instances = eval("self." + child_node.attribute + ".all()")
                for child_instance in child_instances:
                    str_xml += child_instance.to_xml(child_node)
            else:
                child_instance = eval("self." + child_node.attribute)
                str_xml += child_instance.to_xml (child_node)
        return '<' + self.__class__.__name__ + self.serialized_attributes() + '>' + str_xml + '</' + self.__class__.__name__ + '>'

class Entity(WorkflowEntity, SerializableEntity):
    '''
    Every entity has a work-flow; the basic one is the one that allows a method to create an instance
    '''
    #corresponds to the class name
    name = models.CharField(max_length=100L)
    version = models.IntegerField(blank=True)
    app = models.CharField(max_length=100L)
    description = models.CharField(max_length=2000L, blank=True)
    table_name = models.CharField(max_length=255L, db_column='tableName', blank=True) 
    id_field = models.CharField(max_length=255L, db_column='idField', blank=True)
    name_field = models.CharField(max_length=255L, db_column='nameField', blank=True)
    description_field = models.CharField(max_length=255L, db_column='descriptionField', blank=True)
    version_released = models.IntegerField(null=True, db_column='versionReleased', blank=True)
    connection = models.ForeignKey(DBConnection, null=True, blank=True)

class AttributeType(models.Model, SerializableEntity):
    name = models.CharField(max_length=255L, blank=True)
    widgets = models.ManyToManyField('application.Widget', blank=True)

class Attribute(models.Model, SerializableEntity):
    name = models.CharField(max_length=255L, blank=True)
    entity = models.ForeignKey('Entity', null=True, blank=True)
    type = models.ForeignKey('AttributeType')
    def __unicode__(self):
        return self.entity.name + "." + self.name 

class EntityTreeNode(models.Model, SerializableEntity):
    entity = models.ForeignKey('Entity')
    # attribute is blank for the entry point
    attribute = models.CharField(max_length=255L, blank=True)
    child_nodes = models.ManyToManyField('self', blank=True, symmetrical=False)
   
class EntityTree(models.Model, SerializableEntity):
    '''
    It is a tree that defines a set of entities on which we can perform a task; the tree has
    an entry point which is a Node e.g. an entity; from an instance of an entity we can use
    the "attribute" attribute from the corresponding EntityTreeNode to get the instances of
    the entities related to each of the child_nodes. An EntityTree could, for example, tell
    us what to export to xml/json, what to consider as a "VersionableMultiEntity" (e.g. an
    instance of VersionableEntityInstance + an EntityTree where the entry_point points to that instance)
    The name should describe its use
    '''
    name = models.CharField(max_length=200L)
    entry_point = models.ForeignKey('EntityTreeNode')
