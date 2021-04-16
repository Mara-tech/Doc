from toolbox import BaseStep
import os
import time


class Step(BaseStep):
    def __init__(self, step_struct=None):
        super(Step, self).__init__(step_struct)
        self.require_mandatory_parameters()

    def execute(self, output, **kwargs):
        output['step_type'] = 'cmd'
        if hasattr(self, 'name'):
            output['step_name'] = self.name
        output['timestamp'] = int(time.time())
        exit_status = os.system(self.cmd)
        status = 'OK' if exit_status == 0 else 'KO'
        output['status'] = status
        return status

    def require_mandatory_parameters(self):
        if not hasattr(self, 'cmd'):
            raise LookupError("'cmd' attribute is mandatory for 'cmd' tool.")
