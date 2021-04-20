import yaml
import doc_log as log
import utils
import time
import toolbox


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
    flat_dico = merge_and_flatten(**kwargs)
    for k in flat_dico.keys():
        if parameter(k) in data:
            if flat_dico[k] is not None:
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
    elif isinstance(data, int) or isinstance(data, float) or isinstance(data, bool):
        return data
    else:
        raise NotImplementedError(f'Data {data} of type {type(data)} is not handled by solve_placeholders')


CONDITIONAL_NEXT_STEP_KEY = 'next-if'
EXPLODE_SPLIT = ','


def should_explode(conditions: str):
    return EXPLODE_SPLIT in conditions


def explode_next_if_steps(step_list: list):
    if not isinstance(step_list, list):
        # parameter can be a string in this example case :
        # next-if:
        #   OK: ${scenarii.shortcut}
        # The DocEngine.get_scenario() method handle these placeholders
        return step_list

    exploded_list = []
    for step in step_list:  # step is a dict
        exploded_step = {}
        if CONDITIONAL_NEXT_STEP_KEY in step:
            for k, v in step.items():
                #  k is usually one of ['name', 'type', 'next-if'], but also any other property (with value of any kind)
                if k == CONDITIONAL_NEXT_STEP_KEY:
                    exploded_condition = {}
                    for conditions, underlying_steps in v.items():
                        if should_explode(conditions):
                            for single_condition in conditions.split(EXPLODE_SPLIT):
                                exploded_condition[single_condition.strip()] = explode_next_if_steps(underlying_steps)
                        else:
                            exploded_condition[conditions] = explode_next_if_steps(underlying_steps)
                    exploded_step[CONDITIONAL_NEXT_STEP_KEY] = exploded_condition
                else:
                    exploded_step[k] = v
        else:
            # step does not contain next-if => easy copy
            exploded_step = step
        exploded_list.append(exploded_step)
    return exploded_list


def explode_next_if_condition(scenarii: dict):
    exploded_scenarii = {}
    if scenarii:
        for scenario_name, scenario in scenarii.items():  # scenario is a list of steps
            exploded_scenarii[scenario_name] = explode_next_if_steps(scenario)
    return exploded_scenarii


def next_steps(step: dict, last_step_status: str):
    if not step or not last_step_status:
        return []
    conditional_next_dict = step.get(CONDITIONAL_NEXT_STEP_KEY, {})
    if last_step_status in conditional_next_dict:
        return conditional_next_dict[last_step_status]
    return []


def run(scenario: list, output: dict, services: dict, **kwargs):
    for step in scenario:
        step_status = execute_step(step, output, **kwargs)
        run(next_steps(step, step_status), output, services, **kwargs)


def execute_step(step_struct: dict, output: dict, step_cls=None, **kwargs):
    if step_cls is None:
        step_cls = toolbox.find_tool(step_struct, **kwargs)
    step = step_cls(solve_placeholders(step_struct, **step_struct, **kwargs), **kwargs)
    return step.execute(output, **kwargs)


def join_service_steps(step_list: list, services: dict, scenario_name: str, **kwargs):
    if not isinstance(step_list, list):
        # parameter can be a string in this example case :
        # next-if:
        #   OK: ${scenarii.shortcut}
        # The DocEngine.get_scenario() method handle these placeholders
        return step_list

    joined_scenario_list = []
    for step in step_list:  # step is a dict
        if 'service' not in step:
            raise LookupError(f"Step {step.get('name', 'unnamed')} from scenario {scenario_name} "
                              f"must define a 'service' key")
        service_name = step['service']
        if service_name not in services:
            raise LookupError(f"Service {service_name} defined in {scenario_name} is not configured under 'services'")

        joined_scenario = services[service_name].copy()
        # now, these properties may be overriden by scenario definition
        for k, v in step.items():
            if k == CONDITIONAL_NEXT_STEP_KEY:
                joined_condition = {}
                for condition_hook, underlying_steps in v.items():
                    joined_condition[condition_hook] = join_service_steps(underlying_steps, services, scenario_name, **kwargs)
                joined_scenario[CONDITIONAL_NEXT_STEP_KEY] = joined_condition
            else:
                joined_scenario[k] = v
        joined_scenario_list.append(joined_scenario)
    return joined_scenario_list


def join_service_definition(scenarii: dict, services: dict, **kwargs):
    if not scenarii:
        return {}
    if not services:
        return scenarii
    joined_scenarii = {}
    for scenario_name, scenario in scenarii.items():  # scenario is a list of steps
        joined_scenarii[scenario_name] = join_service_steps(scenario, services, scenario_name, **kwargs)
    return joined_scenarii


class DocEngine:

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
        return explode_next_if_condition(  # explode when a next-if key is composed (e.g KO, UNDEFINED)
            solve_placeholders(  # solve properties when possible
                join_service_definition(  # read properties (including 'type') from services
                    solve_placeholders(  # solve scenarii shortcut
                        self.doc_conf.get('scenarii', {}),
                        scenarii=self.doc_conf.get('scenarii', {})
                    ), self.services
                ),
                **self.flattened_properties,
            )
        )

    def get_environments(self, **kwargs):
        return list(k for k, v in self.environments.items())

    def get_services(self, **kwargs):
        return solve_placeholders(self.services, **self.flattened_properties, **kwargs)

    def get_scenarii(self, requested_env, **kwargs):
        if requested_env not in self.environments:
            raise LookupError(f"Environment {requested_env} is not configured, thus unknown.")
        requested_env_conf = self.environments[requested_env]
        if 'scenarii' not in requested_env_conf:
            raise LookupError(f"Environment {requested_env} has no configured scenarii. Please add a 'scenarii' entry in configuration.")
        return self.environments[requested_env]['scenarii']

    def get_properties(self, flat: bool = False, **kwargs):
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
            return solve_placeholders(self.scenarii[scenario_name], **self.properties, env=env)
        else:
            return self.scenarii[scenario_name]

    def run_scenario(self, scenario_name, env='default', solving_ph=True, **kwargs):
        scenario = self.get_scenario(scenario_name, env, solving_ph, **kwargs)
        output = {'scenario': scenario_name, 'environment': env, 'timestamp': int(time.time())}
        run(scenario, output, self.services, **kwargs, **self.properties)
        return output

    def run_scenarii(self, environment, **kwargs):
        output = []
        for scenario in self.get_scenarii(environment, **kwargs):
            output.append(self.run_scenario(scenario, env=environment, **kwargs))
        return output
