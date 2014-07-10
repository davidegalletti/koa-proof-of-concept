from django.db import models

from kag.utils import xmlMinidom
from xml.dom.minidom import Node
from django.db.models.manager import Manager
from django.db.models.related import RelatedObject


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
                if not names == 'pk' and not names.endswith("_id") and not callable(attr) and not issubclass(attr.__class__, RelatedObject) and not issubclass(attr.__class__, Manager) and not names.startswith("_") and not names.endswith("_") and not names in fk:
                    out[names] = str(attr)
        return out
    def serialized_attributes(self):
        attributes = ""
        for key, value in self.serializable_attributes().iteritems():
            attributes += ' ' + key + '="' + value + '"'
        return attributes

    def to_xml(self, etn):
        str_xml = ""
        if etn.full_export:
            for child_node in etn.child_nodes.all():
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
                    str_xml += child_instance.to_xml (child_node)
            return '<' + self.__class__.__name__ + ' ' + self.serialized_attributes() + '>' + str_xml + '</' + self.__class__.__name__ + '>'
        else:
            if etn.entity.name_field <> "":
                xml_name = " " + etn.entity.name_field + "=\"" + getattr(self, etn.entity.name_field) + "\""
            return '<' + self.__class__.__name__ + ' ' + self._meta.pk.attname +'="' + str(self.pk) + '"' + xml_name + '/>'

    def from_xml(self, etn, xmldoc, insert = True):
        pass
#         if not insert:
#             self.pk = xmlMinidom.getNaturalAttribute(xmldoc, 'Id')
#         self.number = xmldoc.attributes["Number"].firstChild.data
#         self.created = xmlMinidom.getStringAttribute(xmldoc, 'Created')
#         self.current = xmlMinidom.getStringAttribute(xmldoc, 'Current')
#         m = Methodology()
#         xml_methodology = xmldoc.getElementsByTagName('Methodology')[0]
#         m.from_xml(xml_methodology, insert)
#         self.methodology = m
#         # I save so I get the ID (if insert == True)
#         self.save()
#         # Pages
#         for xml_child in xmldoc.childNodes:
#             # Some nodes are text nodes (e.g. u'\n     ') I need to look just at ELEMENT_NODE
#             if xml_child.nodeType == Node.ELEMENT_NODE and xml_child.tagName == 'Pages':
#                 xml_pages = xml_child
#                 break
#         for xml_page in xml_pages.childNodes:
#             if xml_page.nodeType == Node.ELEMENT_NODE and xml_page.tagName == 'Page':
#                 p = Page()
#                 p.from_xml(xml_page, self, None, insert)
#         #WeightScenarios
#         xml_weight_scenarios = xmldoc.getElementsByTagName('WeightScenarios')
#         for xml_weight_scenario in xml_weight_scenarios:
#             ws = WeightScenario()
#             ws.from_xml(xml_weight_scenario, self, insert)

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
    def __str__(self):
        return self.entity.name + "." + self.name

class EntityTreeNode(models.Model, SerializableEntity):
    entity = models.ForeignKey('Entity')
    # attribute is blank for the entry point
    attribute = models.CharField(max_length=255L, blank=True)
    child_nodes = models.ManyToManyField('self', blank=True, symmetrical=False)
    # if full_export all attributes are exported, otherwise only the id
    full_export = models.BooleanField(default=True)

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

class UploadedFile(models.Model):
    '''
    Used to save uploaded xml file so that it can be later retrieved and imported
    '''
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')