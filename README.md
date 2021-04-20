# Doc
Issue Detector and Fixer Bot

## Issue Detector Engine
Doc is designed to execute health checks of an application(s).
Everything is described in YAML configuration.
Following sub-sections define what's "Everything", by covering Doc's notions. 

### Environments
Your application probably exists 
(by the way, see [Environment comparator](#environment-comparator) which turns very useful at deployment time)
on several environments (e.g dev, uat, prod). These environment may have different architectures, variables, and checks.
In your `conf.yml` file :

    environments:
        prod:
            scenarii:
                - scenario_1
                - scenario_2
                - scenario_3
            properties:
                foo: bar
        dev:
            scenarii:
                - scenario_1
                - scenario_3
            properties:
                foo: bat
                brol: broc

When "Run scenarii for environment _prod_" is triggered (e.g `POST /doc/prod/scenarii`), 
then 3 scenarii will be executed :
`[scenario_1, scenario_2, scenario_3]`

### Scenarii
Scenarii is a catalog of scenario descriptions.
In your `conf.yml` file :

    scenarii:
        scenario_1:
            - service: check_A
            - service: check_B
        scenario_2:
            - service: check_B
              someProperty: someValue
        scenario_3:
            - service: check_B
              someProperty: anotherValue
              next-if:
                OK:
                    - service: check_C
                KO:
                    - serice: check_D

This is a preview of what's being detailed in the [next section](#scenario).

### Scenario
A scenario configuration can be seen as a tree.
Basic usage is a list of steps to execute, one after the previous (this is the reason of the `-`).
In order to find an issue root cause efficiently, 
one will understand that Doc likes to execute a step according to the result of the previous one.
This is the idea behind the key-word `next-if`. An example to easily understand.

    scenarii:
        scenario_1:
            - service: check_A
              next-if:
                OK:
                    - service: check_B
                KO, UNDEFINED:
                    - serice: check_C
            - service: check_D

In the above example, the executed step at a specific time depends of output status of `check_A`.
If output status is `OK`, then executed steps for `scenario_1` are `[check_A, check_B, check_D]`.
If output status is `KO` or `UNDEFINED`, then executed steps for `scenario_1` are `[check_A, check_C, check_D]`.
If output status is something else, then executed steps for `scenario_1` are `[check_A, check_D]`.

Indeed, a step (an executed instance of a [service](#service)) has a single output status 
(besides of writing in an `output` structure, final result of a scenario/scenarii execution).
A status a string, usually `OK` or `KO`, but completely free and defined in the [tool (service implementation)](#tool).

As you may have noticed, each step __MUST__ at least have `service` key.
The service value refers to what's defined in the [next section](#service).

### Service
Services describe quite closely what will actually be done. 
It is an elementary operation in the YAML configuration scope.
Indeed, a step is an instance of a service. 
In fact, a __mandatory__ `type` property is expected, in order to know what code will be executed.
Then, one type may require other propertie(s) (such as `cmd` for `type: cmd` ; e.g `cmd: "echo brol"`).
One may think of a Service as an elementary health check, such as, like in your `conf.yml` file :

    services:
        check-ps:
            type: cmd
            cmd: "ps aux | grep my-app"
        check-spring-boot:
            type: api.rest.get
            url: ${my-app-url}/actuator/health
        check-logs:
            type: cmd
            cmd: "grep ERROR ${my-app-path}/logs/my-app.log"
            
When defining a service, choose an existing [tool](#tool) or create your own,
in [toolbox package](doc/src/toolbox).

### Tool
Tool is the actual implementation (in Python).
The tool __must__ define an `execute(output, **kwargs)` method 
- taking `output` and `kwargs` dictionaries
- and returning an Output status (`str`)
(used to know what will be next step to execute, in case `next-if` property is defined).

This method responsible for writing anything useful in this output structure (which passes from a step to the next)
and is the final result of a scenario/scenarii execution.
This kind of implementation (say in `toolbox/some/fancy/tool/__init__.py`) is strongly recommended :

    from toolbox.some.amazing.tool import Step as ParentStep

    class Step(ParentStep):
        def __init__(self, step_struct=None, **kwargs):
            super(Step, self).__init__(step_struct, **kwargs)
            self.require_mandatory_parameters()
            
        def require_mandatory_parameters(self):
            super(Step, self).require_mandatory_parameters()
            if not hasattr(self, 'some_mandatory_property'):
                raise LookupError("'some_mandatory_property' attribute is mandatory for 'some.fancy.tool' tool.")

        def execute(self, output, **kwargs):
            # DO SOMETHING HERE
            # ADD ANYTHING IN output[self.get_service_name()]
            # RETURN STATUS
            fancy_output = {'question': 'What is your quest ?', 'answer': 'To seek the Holy Grail.'}
            output[self.get_service_name()] = fancy_output
            return 'OK'
            

Explore the [toolbox package](doc/src/toolbox) and create your own tool
if your needs are not covered by the existing ones.
In this case, please follow these few rules :
- Create Python package and put your implementation in the `__init__.py` file
- Create a class `Step` that extends [BaseStep](doc/src/toolbox/__init__.py) or another defined tool

Your implementation will be accessible if the service has the appropriate `type`.
For example, 

    toolbox/
        some/
            __init__.py
            fancy/
                __init__.py
                tool/
                    __init__.py     <<-- defines a class Step()
                    
is accessible with `type: some.fancy.tool`.

#### Command
`type: cmd`

Requires property `cmd`.

The command is executed from a subprocess shell.

Output status :
- if exit_status is 0, then `OK`
- else `KO` 

Output written :
- `stdout`
- `stderr`

#### HTTP requests
`type: api`
`type: api.rest`
`type: api.rest.get`
`type: api.rest.post`

Requires property `url`.

The HTTP request is executed from `requests` Python package.

Output status :
- if 200 <= status_code < 300, then `OK`
- else `KO`

Output written :
- `json` : response body as a string
- `json_obj` : response body as a JSON object

##### Subtype `type: api.rest.get.extract`
Additional required property `extract`, of type string or list.

Output written :
- if `extract` property is single (string type), then the value of this property.
- if `extract` property is multiple (list type), then a mapping of these properties.

Refer to [unit test](doc/tests/unit/test_run_api_get_extract.py) and associated [conf file](doc/tests/unit/test_run_api_get_extract.yml) for an example.

### Properties
Properties entries may be considered as global properties. This is usually useful to define URLs and hostnames.
In your `conf.yml` file :

    properties:
      my-app:
        url: http://example.com/
      github:
          prod:
            base_url: https://api.github.com
          dev:
            base_url: https://dev.api.github.com

Anywhere in the configuration, this can be referred to, like for example :

    services:
        check_github:
            type: api.rest.get
            url: ${github.${env}.base_url}/health  <<-- will be replaced with a valid URL 
            someProperty: ${my-app.url} 

In the above example, Doc engine will be able to replace the pointed line with a valid URL 
when an `environment` variable is given, for example when executing a scenario/scenarii on one environment
(e.g `POST /doc/dev/scenarii`).

As you may have noticed, custom properties can also be defined in `environment`, `services` and `scenario` definition.
If property key overlap (same key defined in several places), then the property value will be solved in this order :
1. environment
2. scenario
3. service
4. properties

This is indeed from the most specific to the most general scope.

#### Refer to another scenario
In order to avoid huge configuration, you may refer a defined scenario.
Do not be confused with expected map or list types (beware of `-`).

    scenarii:
        scenario_2:
            - service: check_B
              someProperty: someValue
        scenario_3:
            - service: check_B
              someProperty: anotherValue
              next-if:
                OK: ${scenarii.scenario_2}   <<-- Shortcut here
                KO:
                    - serice: check_D
        

### Next to be done...
Combine Doc to a contact interface (e-mail, Teams, etc.)
in order to warn user groups according found status during an execution.
Example : During a night execution, alert on-duty team an unexpected (status KO) behavior ;
asking the teammate to take (fix) the issue, and alternatively to auto-fix the issue. 

    
## Environment comparator
Still to be done...
Very valuable for CI/CD : Doc can validate or invalidate a deployed environment on a simple trigger 
(e.g `POST /doc/cicd_env/compare/ref_env`).

## Issue Fixer Bot
An easy use-case is to describe a service supposed to fix an issue. E.g :

    scenarii:
        is-server-up:
            - service: check-server-up
              next-if:
                KO:
                  - service: restart-server
                  
    services:
        check-server-up:
            type: cmd
            cmd: "ps aux | grep my-app"
        restart-server:
            type: cmd
            cmd: "./my-app start"
            
Advanced use-cases tend to ask human permission before executing a fixing scenario/service.

## Learning Bot
The idea is to persist outputs of recurrent (say a cron) scenario executions.
Doc may find and analyze patterns leading to errors.
Thus, when some executions look like these patterns, 
Doc may warn (and possibly prevent) that the environment is likely to evolve to an error.
