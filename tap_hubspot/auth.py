"""HubSpot Authentication."""

import sys

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class HubSpotOAuthAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for HubSpot."""

    @override
    @property
    def oauth_request_body(self):  # noqa: ANN201
        return {
            "grant_type": "refresh_token",
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "refresh_token": self.config["refresh_token"],
        }
