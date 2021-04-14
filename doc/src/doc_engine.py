import yaml
import doc_log as log
import utils

class DocEngine():

    def __init__(self, conf_filename):
        super(DocEngine, self).__init__()
        self.conf_filename = conf_filename

    @property
    def doc_conf(self):
        with open(self.conf_filename, 'r') as file:
            log.debug(f'Parsing conf from {file.name}.')
            doc_conf = yaml.load(file, Loader=yaml.FullLoader)

        if doc_conf is None:
            doc_conf = {}
        return doc_conf

    @property
    def environments(self):
        return self.doc_conf.get('environments', {})

    @property
    def properties(self):
        return self.doc_conf.get('properties', {})

    @property
    def flattened_properties(self):
        return utils.flatten(self.properties)

    @property
    def services(self):
        return self.doc_conf.get('services', {})

    @property
    def scenarii(self):
        return self.doc_conf.get('scenarii', {})

    def get_environments(self, **kwargs):
        return list(k for k, v in self.environments.items())

    def get_services(self, args, **kwargs):
        """
        TODO by introspection of scenarii
        :param args:
        :return:
        """
        # if 'environment' not in args:
        #     raise KeyError("Expected key 'environment' not provided.")
        # requested_env = args['environment']
        # if requested_env not in self.environments:
        #     raise KeyError(f"Environment {requested_env} is not configured, thus unknown.")
        # requested_env_conf = self.environments[requested_env]
        # if 'services' not in requested_env_conf:
        #     raise KeyError(f"Environment {requested_env} has no configured services. Please add a 'services' entry in configuration.")
        # return self.environments[requested_env]['services']
        return {}

    def get_scenarii(self, requested_env, **kwargs):
        if requested_env not in self.environments:
            raise KeyError(f"Environment {requested_env} is not configured, thus unknown.")
        requested_env_conf = self.environments[requested_env]
        if 'scenarii' not in requested_env_conf:
            raise KeyError(f"Environment {requested_env} has no configured scenarii. Please add a 'scenarii' entry in configuration.")
        return self.environments[requested_env]['scenarii']

    def get_properties(self, flat:bool=False, **kwargs):
        if flat:
            return self.flattened_properties
        else:
            return self.properties
