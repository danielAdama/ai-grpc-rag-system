
import os
import yaml


class Configuration:
    def __init__(self):
        self.config = None
        # Load the configuration from the YAML file
        self.load_config()

    def load_config(self):
        # Get the absolute path to the root directory of the project
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Construct the path to the configuration file
        config_file = os.path.join(root_dir, 'env_config', 'app_config.yml')
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
