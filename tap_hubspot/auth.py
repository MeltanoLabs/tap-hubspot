"""HubSpot Authentication."""

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


class HubSpotOAuthAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for HubSpot."""

    @property
    def oauth_request_body(self):  # noqa: ANN201, D102
        return {
            "grant_type": "refresh_token",
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "refresh_token": self.config["refresh_token"],
        }
