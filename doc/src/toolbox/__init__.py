import doc_log as log
import importlib
STEP_TYPE_KEY = 'type'


class BaseStep:
    def __init__(self, step_struct=None):
        super(BaseStep, self).__init__()
        if step_struct is None:
            step_struct = {}
        for k,v in step_struct.items():
            setattr(self, k, v)
        if hasattr(self, 'args'):
            log.warn(f'Attribute args will be overridden for step {self.name if hasattr(self, "name") else "UNNAMED"}')
        self.args = step_struct

    def __eq__(self, other):
        if not other or not self.__class__ == other.__class__:
            return False
        for self_arg, other_arg in zip(self.args, other.args):
            if not self_arg == other_arg:
                return False
        return True


class DefaultStep(BaseStep):
    def __init__(self, step_struct=None):
        super(DefaultStep, self).__init__(step_struct)


def find_tool(step_struct: dict, **kwargs):
    if step_struct:
        if STEP_TYPE_KEY in step_struct:
            step_type = step_struct[STEP_TYPE_KEY]
            log.debug(f'Looking for type {step_type} object to instantiate.')
            # https://docs.python.org/3/library/importlib.html?highlight=importlib#importlib.import_module
            target_module = importlib.import_module(f'..{step_type}', package=f'{__package__}.subpkg')
            # The module is expected to define a class called 'Step'
            cls = getattr(target_module, 'Step')
            return cls
    return DefaultStep
