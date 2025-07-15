import logging

from typing import Annotated, Dict
from semantic_kernel.functions import kernel_function

import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential

from .base_plugin import BasePlugin

class ServiceBusPlugin(BasePlugin):
    
    def __init__(self, settings : Dict= {}):
        """
        Initialize the Service Bus Plugin with the provided settings.
        """
        super().__init__(settings)

        self.fully_qualified_namespace = settings.get("fully_qualified_namespace", "YOUR_SERVICE_BUS_NAMESPACE.servicebus.windows.net")
        self.topic_name = settings.get("topic_name", "YOUR_TOPIC_NAME")
        self.queue_name = settings.get("queue_name", "YOUR_QUEUE_NAME")

        self.client = ServiceBusClient(
        fully_qualified_namespace=self.fully_qualified_namespace,
        credential=self.config.credential,
        logging_enable=True)
        
        # get a Queue Sender object to send messages to the queue
        self.sender = self.client.get_queue_sender(queue_name=self.queue_name)

    @kernel_function(
        name=f"send_servicebus_message",
        description="Send a message to an Azure Service Bus queue.",
    )
    async def send_servicebus_message(self, message: str):
        # Create a Service Bus message and send it to the queue
        sb_message = ServiceBusMessage(message)
        await self.sender.send_messages(sb_message)

        logging.info(f"Message sent to Service Bus queue '{self.queue_name}': {message}")
    