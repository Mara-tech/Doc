from toolbox import BaseStep
import time
import requests
import json


class Step(BaseStep):
    JSON_STR_KEY = 'json'
    JSON_OBJ_KEY = 'json_obj'

    def __init__(self, step_struct=None, method='get', headers=None, **kwargs):
        super(Step, self).__init__(step_struct, **kwargs)
        if headers is None:
            headers = {}
        self.require_mandatory_parameters()
        self.method = method
        self.headers = self.merge_headers(headers, getattr(self, 'headers', {}))

    def require_mandatory_parameters(self):
        if not hasattr(self, 'url'):
            raise LookupError("'url' attribute is mandatory for 'api' tool.")

    def execute(self, output, **kwargs):
        step_output = {
            'step_type': self.type,
            'timestamp': int(time.time()),
            'url': self.url
        }

        payload = json.loads(self.payload) if hasattr(self, 'payload') else None

        resp = requests.request(self.method, self.url, json=payload, headers=self.headers)

        response_code = resp.status_code
        response_body = resp.content
        step_output[self.JSON_STR_KEY] = response_body.decode('UTF-8').strip()
        step_output[self.JSON_OBJ_KEY] = json.loads(response_body)

        status = 'OK' if 200 <= response_code < 300 else 'KO'
        step_output['status'] = status
        step_output['end_time'] = int(time.time())
        output[self.get_service_name()] = step_output
        return status

    def merge_headers(self, from_init: dict, from_step_definition: dict):
        # from_step_def priority
        merge = from_step_definition.copy()
        for k,v in from_init.items():
            if k not in merge:
                merge[k] = v
        return merge
