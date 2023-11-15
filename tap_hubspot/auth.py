"""HubSpot Authentication."""

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


class HubSpotOAuthAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for HubSpot."""

    @property
    def oauth_request_body(self):
        return {
            "grant_type": "refresh_token",
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "refresh_token": self.config["refresh_token"],
        }

    @classmethod
    def create_for_stream(cls, stream):
        return cls(
            stream=stream,
            auth_endpoint="https://api.hubapi.com/oauth/v1/token",
        )