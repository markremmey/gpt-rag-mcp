from typing import Dict, Optional
from semantic_kernel.functions import kernel_function

from .msgraph import MicrosoftGraphPlugin

class MicrosoftTeamsPlugin(MicrosoftGraphPlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)
        
        self.team_id = self.settings.get('team_id', None)
        self.channel_id = self.settings.get('channel_id', None)

        self.client_id = self.settings.get('client_id', None)
        self.client_secret = self.settings.get('client_secret', None)
        self.tenant_id = self.settings.get('tenant_id', None)

        self.scope = self.settings.get('scope', 'https://graph.microsoft.com/.default')
        self.has_oauth_endpoint = True
        self.oauth_token_endpoint = f"/oauth2/msteams/token"
        self.oauth_authorize_endpoint = f"/oauth2/msteams/authorize"

    @kernel_function(
        name="add_msteams_channel_message",
        description="Adds a message to a Microsoft Teams channel.",
    )
    def add_msteams_channel_message(self, 
        user_prompt: str,
        team_id : Optional[str] = None,
        channel_id : Optional[str] = None):
        """
        Adds a message to a Microsoft Teams channel.
        """

        if not team_id:
            team_id = self.team_id
        if not channel_id:  
            channel_id = self.channel_id

        _get_user_context = self._get_user_context()

        #use the access token from the user context if available
        if _get_user_context:
            self.access_token = _get_user_context.get("access_token", None)

        url =  f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages"

        message = {
            "body": {
                "content": user_prompt
            }
        }

        response = self.run_msgraph_query(url, body=message, method="POST")

        return response

    @kernel_function(
        name="add_msteams_channel_message_reply",
        description="Adds a reply to a message in a Microsoft Teams channel.",
    )
    def add_msteams_channel_message_reply(self, 
        user_prompt: str,
        team_id : Optional[str] = None,
        channel_id : Optional[str] = None,
        message_id : str = None):
        """
        Adds a message to a Microsoft Teams channel.
        """

        _get_user_context = self._get_user_context()

        #use the access token from the user context if available
        if _get_user_context:
            self.access_token = _get_user_context.get("access_token", None)

        if not team_id:
            team_id = self.team_id
        if not channel_id:
            channel_id = self.channel_id
        
        if not message_id:
            raise ValueError("message_id must be provided")

        url =  f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"

        message = {
            "body": {
                "content": user_prompt
            }
        }

        response = self.run_msgraph_query(url, body=message, method="POST")

        return response

    @kernel_function(
        name="add_msteams_chat_message",
        description="Adds a reply to a message in a Microsoft Teams channel.",
    )
    def add_msteams_chat_message(self, 
        user_prompt: str,
        chat_id : str = None):
        """
        Adds a message to a Microsoft Teams channel.
        """

        _get_user_context = self._get_user_context()

        #use the access token from the user context if available
        if _get_user_context:
            self.access_token = _get_user_context.get("access_token", None)

        url =  f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"

        message = {
            "body": {
                "content": user_prompt
            }
        }

        response = self.run_msgraph_query(url, body=message, method="POST")

        return response