from core.production_unit import NoWorkerToPerformAction, InvalidInputLoaded

class OperationalConstraint(object):
    def __init__(self, operation):
        self.operation = operation


class HasWorkerConstraint(OperationalConstraint):
    def validate(self, worker=None):
        if not worker:
            raise NoWorkerToPerformAction()


class InputValidForSpecConstraint(OperationalConstraint):
    def validate(self, worker=None):
        if not self.operation.production_unit.spec.validate_any(self.operation.inputs):
            raise InvalidInputLoaded()
