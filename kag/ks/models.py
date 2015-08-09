from django.db import models
from entity.models import SerializableSimpleEntity


class EventType(SerializableSimpleEntity):
    '''
    '''
    
class Event(SerializableSimpleEntity):
    '''
    Something you want to get notified about; so you can subscribe to a type of event for 
    a specific data set / EntityInstance
    '''
    entity_instance_uri = models.CharField(max_length=2000L)
    root_instance_uri = models.CharField(max_length=2000L)
    event_type = models.ForeignKey(EventType)

class Subscriber(SerializableSimpleEntity):
    '''
    '''

class Subscription(SerializableSimpleEntity):
    '''
    '''
    root_instance_uri = models.CharField(max_length=2000L)

class NotificationReceived(SerializableSimpleEntity):
    '''
    '''

class Notification(SerializableSimpleEntity):
    '''
    '''
