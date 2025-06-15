import msal
import requests

from typing import Dict
from semantic_kernel.functions import kernel_function

from .base_plugin import BasePlugin

class MicrosoftGraphPlugin(BasePlugin):
    def __init__(self, settings : Dict= {}):

        super().__init__(settings)

        self.client_id = self.settings.get('client_id', None)
        self.client_secret = self.settings.get('client_secret', None)
        self.tenant_id = self.settings.get('tenant_id', None)
        self.username = self.settings.get('username', None)
        self.password = self.settings.get('password', None)
        self.access_token = None

        self.graph_url = self.settings.get('graph_url', 'https://graph.microsoft.com/v1.0')
        self.authority = self.settings.get('authority', f'https://login.microsoftonline.com/{self.tenant_id}')

        self.scope = self.settings.get('scope', 'https://graph.microsoft.com/.default')
        self.has_oauth_endpoint = True
        self.oauth_token_endpoint = f"/oauth2/msgraph/token"
        self.oauth_authorize_endpoint = f"/oauth2/msgraph/authorize"

        self.cache = msal.SerializableTokenCache()

    def handle_oauth_token(scope, send, receive):
        pass

    def handle_oauth_authorize(scope, send, receive):
        pass

    def _build_msal_app(self, cache=None):
        # Use the asynchronously retrieved client secret
        return msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
            token_cache=cache
        )

    def get_valid_access_token(self, scopes):
        msal_app = self._build_msal_app(cache=self.cache)
        accounts = msal_app.get_accounts()
        account = accounts[0] if accounts else None
        
        if not account:
            result = msal_app.acquire_token_for_client(scopes=scopes)
        else:
            result = msal_app.acquire_token_silent(scopes, account=account)

        if not result:
            raise Exception("Could not refresh token silently: no token found in cache.")
        if "error" in result:
            raise Exception(result.get("error_description", "Could not refresh token silently."))
        
        return result.get("access_token")

    def authenticate(self):
        """
        Authenticate with Microsoft Graph API.
        This method should be implemented in subclasses.
        """
        if self.username and self.password:
            # If username and password are provided, use them to get an access token
            self.access_token = self.get_access_token_user()
        else:
            self.access_token = self.get_valid_access_token(scopes=["https://graph.microsoft.com/.default"])

    def get_access_token_user(self):
        url =f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        payload = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "username": self.username,
            "password": self.password
        }
        response = requests.post(url, data=payload)
        response_data = response.json()
        print(response_data)
        access_token = response_data['access_token']
        #print(access_token)
        return access_token
    
    @kernel_function(
        name="run_msgraph_query",
        description="Runs a graph query with the given prompt.",
    )
    def run_msgraph_query(self, 
        url: str,
        body: Dict = None,
        method: str = "GET",
        headers: Dict = None
    ):
        """
        Runs a graph query with the given prompt.
        """

        _get_user_context = self._get_user_context()

        if not self.access_token:
            self.authenticate()

        if headers is None:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

        if body is None:
            body = {}

        # Here you would typically use a library like requests to make the HTTP request
        response = requests.request(method, url, headers=headers, json=body)
        if response.status_code not in [200, 201]:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        
        return response.json()