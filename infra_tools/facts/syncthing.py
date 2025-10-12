# pyinfra fact: retrieve Syncthing configuration

import json
from pyinfra.api import FactBase


class SyncthingConfig(FactBase):
    """
    Retrieve Syncthing configuration as a dictionary.

    Returns the complete Syncthing configuration by running 'syncthing cli config dump-json'.
    """

    command = "syncthing cli config dump-json"

    def process(self, output):
        """
        Process the JSON output from syncthing cli config dump-json command.

        Args:
            output (list): Command output lines

        Returns:
            dict: Parsed Syncthing configuration or None if parsing fails
        """
        if not output:
            return None

        try:
            # Join all output lines and parse as JSON
            json_str = '\n'.join(output)
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            # Return None if JSON parsing fails
            return None
