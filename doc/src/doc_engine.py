

class DocEngine():

    def __init__(self, doc_conf=None):
        super(DocEngine, self).__init__()
        if doc_conf is None:
            doc_conf = {}

        self.properties = doc_conf.get('properties', {})
        self.services = doc_conf.get('services', {})
        self.scenarii = doc_conf.get('scenarii', {})
        self.environments = doc_conf.get('environments', {})

        """
        or ?
        for k,v in doc_conf.items():
            setattr(self, k, v)
        """

    def get_environments(self):
        return list(k for k,v in self.environments.items())

    def get_services(self, args):
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

    def get_scenarii(self, requested_env):
        if requested_env not in self.environments:
            raise KeyError(f"Environment {requested_env} is not configured, thus unknown.")
        requested_env_conf = self.environments[requested_env]
        if 'scenarii' not in requested_env_conf:
            raise KeyError(f"Environment {requested_env} has no configured scenarii. Please add a 'scenarii' entry in configuration.")
        return self.environments[requested_env]['scenarii']

