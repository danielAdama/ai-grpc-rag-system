
import os
import yaml
from config import BASE_DIR

class Configuration:
    def __init__(self):
        self.config = None
        # Load the configuration from the YAML file
        self.load_config()

    def load_config(self):
        # Construct the path to the configuration file
        config_file = os.path.join(str(BASE_DIR), 'env_config', 'app_config.yml')
        # Load the configuration from the YAML file
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def get_config(self, key):
        """
        Get the value of the specified key from the configuration.
        :param key: The key to retrieve from the configuration.
        :type key: str
        :return: The value of the specified key, or None if the key is not found in the configuration.
        :rtype: any
        """
        return self.config[key] if key in self.config else None
