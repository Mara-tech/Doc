import yaml
import doc_log as log
import utils


def parameter(param):
    return '${' + param + '}'


def merge_dicos(**kwargs):
    return dict(kwargs)


def merge_and_flatten(**kwargs):
    return utils.flatten(merge_dicos(**kwargs))


def should_replace_object(data, k, v):
    '''
    Purpose is such that
    Given
    data = '${my-scenario}'
    {k:v} = {'my-scenario': {'name':'some-check', 'next-if': {'OK': [{'name': 'another-check'}]}} }
    Then
    returned object is v (instead of using str.replace() function).
    '''
    full_placeholder = parameter(k) == data
    can_handle_object = isinstance(v, dict) or isinstance(v, list)
    return full_placeholder and can_handle_object


def replace(data, **kwargs):
    for k, v in merge_and_flatten(**kwargs).items():
        if parameter(k) in data:
            if should_replace_object(data, k, v):
                # object replacement
                data = v
            else:
                # alter string using str.replace()
                data = data.replace(parameter(k), str(v), 1)
    return data


def can_replace(data, **kwargs):
    for k in merge_and_flatten(**kwargs).keys():
        if parameter(k) in data:
            return True
    return False


def replace_all_placeholders(data, **kwargs):
    while can_replace(data, **kwargs):
        data = replace(data, **kwargs)
    return data


def solve_placeholders(data, **kwargs):
    if isinstance(data, str):
        return replace_all_placeholders(data, **kwargs)
    elif isinstance(data, dict):
        # return {replace_all_placeholders(k, **kwargs): replace_all_placeholders(v, **kwargs) for k, v in data.items()}
        return {k: solve_placeholders(v, **kwargs) for k, v in data.items()}
    elif isinstance(data, list):
        return list(solve_placeholders(item, **kwargs) for item in data)
    else:
        raise NotImplementedError(f'Data {data} of type {type(data)} is not handled by solve_placeholders')


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
            raise LookupError(f"Environment {requested_env} is not configured, thus unknown.")
        requested_env_conf = self.environments[requested_env]
        if 'scenarii' not in requested_env_conf:
            raise LookupError(f"Environment {requested_env} has no configured scenarii. Please add a 'scenarii' entry in configuration.")
        return self.environments[requested_env]['scenarii']

    def get_properties(self, flat:bool=False, **kwargs):
        if flat:
            return self.flattened_properties
        else:
            return self.properties

    def get_scenario(self, scenario_name, env=None, solving_ph=True, **kwargs):
        if scenario_name not in self.scenarii:
            raise LookupError(f"Scenario {scenario_name} is not configured, thus unknown.")
        if env is not None and env not in self.environments:
            raise LookupError(f"Environment {env} is not configured, thus unknown.")
        if env is not None and scenario_name not in self.environments[env]['scenarii']:
            raise LookupError(f'Scenario {scenario_name} is not defined for environment {env}.')
        if solving_ph:
            return solve_placeholders(self.scenarii[scenario_name], **self.properties, scenarii=self.scenarii, env=env)
        else:
            return self.scenarii[scenario_name]
