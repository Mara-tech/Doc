from toolbox.api.rest import Step as RestStep


class Step(RestStep):
    def __init__(self, step_struct=None, **kwargs):
        super(Step, self).__init__(step_struct, method='get', **kwargs)
