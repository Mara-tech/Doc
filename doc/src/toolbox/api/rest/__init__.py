from toolbox.api import Step as ApiStep


class Step(ApiStep):
    def __init__(self, step_struct=None, **kwargs):
        super(Step, self).__init__(step_struct, headers={'Content-type': 'application/json'}, **kwargs)
