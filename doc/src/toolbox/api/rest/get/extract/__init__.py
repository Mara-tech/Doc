from toolbox.api.rest.get import Step as GetStep
import doc_log as log


class Step(GetStep):
    def __init__(self, step_struct=None, **kwargs):
        super(Step, self).__init__(step_struct, **kwargs)
        self.require_mandatory_parameters()

    def require_mandatory_parameters(self):
        super(Step, self).require_mandatory_parameters()
        if not hasattr(self, 'extract'):
            raise LookupError("'extract' attribute is mandatory for 'api.rest.get.extract' tool.")

    def execute(self, output, **kwargs):
        status = super(Step, self).execute(output, **kwargs)
        if isinstance(self.extract, str):
            if self.can_extract(self.extract, output):
                output[self.get_service_name()] = output[self.get_service_name()][self.JSON_OBJ_KEY][self.extract]
            else:
                log.warn(f'Extract service could not find key {self.extract} in output[{self.get_service_name()}][{self.JSON_OBJ_KEY}]')
            pass
        elif isinstance(self.extract, list):
            if self.have_extracts(self.extract, output):
                extraction = {}
                for extract_key in self.extract:
                    extraction[extract_key] = output[self.get_service_name()][self.JSON_OBJ_KEY].get(extract_key, 'Cannot find key')
                output[self.get_service_name()] = extraction
            else:
                log.warn(f'Extract service could not find any key from {self.extract} in output[{self.get_service_name()}][{self.JSON_OBJ_KEY}]')
        else:
            log.error(f"Extract service does not support type {type(self.extract)} as 'extract' key.")

        return status

    def can_extract(self, key: str, output: dict):
        return self.get_service_name() in output \
               and self.JSON_OBJ_KEY in output[self.get_service_name()] \
               and key in output[self.get_service_name()][self.JSON_OBJ_KEY]

    def have_extracts(self, keys: list, output: dict):
        for extract_key in keys:
            if self.can_extract(extract_key, output):
                return True
