from toolbox import BaseStep
import subprocess
import time


class Step(BaseStep):
    def __init__(self, step_struct=None):
        super(Step, self).__init__(step_struct)
        self.require_mandatory_parameters()

    def execute(self, output, **kwargs):
        step_output = {
            'step_type': self.type,
            'timestamp': int(time.time()),
            'cmd': self.cmd
        }
        completed_process = subprocess.run(self.cmd, shell=True, capture_output=True)
        exit_status = completed_process.returncode
        step_output['stdout'] = completed_process.stdout.decode('UTF-8').strip()
        step_output['stderr'] = completed_process.stderr.decode('UTF-8').strip()
        status = 'OK' if exit_status == 0 else 'KO'
        step_output['status'] = status
        step_output['end_time'] = int(time.time())
        output[self.get_service_name()] = step_output
        return status

    def require_mandatory_parameters(self):
        if not hasattr(self, 'cmd'):
            raise LookupError("'cmd' attribute is mandatory for 'cmd' tool.")
