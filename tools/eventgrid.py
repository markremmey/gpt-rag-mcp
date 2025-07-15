import logging

from typing import Annotated, Dict
from semantic_kernel.functions import kernel_function

from .base_plugin import BasePlugin

from azure.core.messaging import CloudEvent
from azure.eventgrid import EventGridPublisherClient, EventGridEvent

class EventGridPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):
        """
        Initialize the Event Grid Plugin with the provided settings.
        """
        super().__init__(settings)

        self.endpoint = settings.get("endpoint", "YOUR_EVENTGRID_TOPIC_ENDPOINT")
        self.topic_name = settings.get("topic_name", "YOUR_EVENTGRID_TOPIC_NAME")

        self.client = EventGridPublisherClient(self.endpoint, self.config.credential)

    @kernel_function(
        name=f"send_eventgrid_event",
        description="Send an event to Azure Event Grid.",
    )
    def send_event(self, type:str, source:str, data:Dict):
        """
        Send an event to Azure Event Grid.
        
        :param event: The event data to send.
        """
        # This method should be implemented to send events to Azure Event Grid
        # using the Azure SDK for Python or any other method as per your requirements.

        event = CloudEvent(
            type=type,
            source=source,
            data=data
        )

        self.client = EventGridPublisherClient(self.endpoint, self.config.credential, namespace_topic=self.topic_name)
        self.client.send(event)