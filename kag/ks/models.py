from django.db import models
from entity.models import SerializableSimpleEntity, EntityInstance


class EventType(SerializableSimpleEntity):
    '''
    '''
    name = models.CharField(max_length=150L)
    description = models.CharField(max_length=2000L,null=True,blank=True)
    
class Event(SerializableSimpleEntity):
    '''
    Something that has happened to a specific instance and you want to get notified about; 
    so you can subscribe to a type of event for a specific data set / EntityInstance
    '''
    # The EntityInstance
    entity_instance = models.ForeignKey(EntityInstance)
    # the event type
    event_type = models.ForeignKey(EventType)
    # when it was fired
    timestamp = models.DateTimeField(auto_now_add=True)

class Subscriber(SerializableSimpleEntity):
    '''
    It can be a KS or any other software
    '''
    # where to send the notification; URI, in the case of a KS, will be something like http://rootks.thekoa.org/notify
    # the actual notification will have the URIInstance of the EntityInstance and the URIInstance of the EventType
    URI = models.CharField(max_length=200L)
    

class SubscriptionToThis(SerializableSimpleEntity):
    '''
    The subscriptions other systems make to my data
    '''
    root_instance_uri = models.CharField(max_length=2000L)
    # the remote ur I have to invoke to notify
    remote_url = models.CharField(max_length=200L)

class Notification(SerializableSimpleEntity):
    '''
    When an event happens for an instance, for each corresponding subscription
    I create a  Notification; cron will send it and change its status to sent
    '''
    event = models.ForeignKey(Event)
    sent = models.BooleanField(default=False)
    subscriber = models.ForeignKey(Subscriber)




class SubscriptionToOther(SerializableSimpleEntity):
    '''
    The subscriptions I make to other systems' data
    '''
    # The URIInstance I am subscribing to 
    URI = models.CharField(max_length=200L)
    root_URI = models.CharField(max_length=200L)
    

class NotificationReceived(SerializableSimpleEntity):
    '''
    When I receive a notification it is stored here and processed asynchronously in cron 
    '''
    # URI to fetch the new data
    URI_to_updates = models.CharField(max_length=200L)
    processed = models.BooleanField(default=False)

class ApiReponse():
    '''
    
    '''
    def __init__(self, status = "", message = ""):
        self.status = status
        self.message = message
        
    def json(self):
        ret_str = '{ "status" : "' + self.status + '", "message" : "' + self.message + '"}'
        return ret_str