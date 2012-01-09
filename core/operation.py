from core.material import Material
from core.output import Output
from core.production_unit import IllegalStateToPerformAction, ProductionUnit, NoWorkerToPerformAction, InvalidInputLoaded, CannotPerformOperation, ProductionUnitSTARTEDState, ProductionUnitIDLEState, CannotProduce, ProductionUnitPRODUCINGState

class Operation(object):
    def __init__(self, production_unit=None):
        self.production_unit = production_unit
        self.constraints = []

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def check_all(self):
        self.check_valid_state()
        self.check()

    def check_valid_state(self):
        if not self.production_unit.get_state() in self.valid_state:
            raise IllegalStateToPerformAction()

    def check_constraints(self):
        for constraint in self.constraints:
            if not constraint.validate(self.production_unit):
                raise CannotPerformOperation(constraint.get_message())


class LoadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]

    def __init__(self, inputs, production_unit=None):
        self.inputs = inputs
        super(LoadOperation, self).__init__(production_unit)

    def check(self):
        if not self.production_unit.worker:
            raise NoWorkerToPerformAction()
        if not self.production_unit.spec.validate_any(self.inputs):
            raise InvalidInputLoaded()

    def perform(self):
        self.production_unit.inputs.append(self.inputs)


class StartOperation(Operation):
    valid_state = [ProductionUnit.IDLE]

    def check(self):pass

    def perform(self):
        for constraint in self.constraints:
            if not constraint.validate(self.production_unit):
                raise CannotPerformOperation()
        self.production_unit.set_state(ProductionUnitSTARTEDState)


class ProduceOperation(Operation):
    valid_state = [ProductionUnit.STARTED, ProductionUnit.PRODUCING]

    def __init__(self, production_time, production_unit=None):
        self.production_time = production_time
        self.progress = 0
        super(ProduceOperation, self).__init__(production_unit)

    def check(self):pass

    def perform(self):
        if not self.production_unit.get_state() == ProductionUnit.PRODUCING:
            self.production_unit.set_state(ProductionUnitPRODUCINGState)

        inputs = self.production_unit.inputs
        spec = self.production_unit.spec
        while self.production_time > 0:
            if not spec.validate_all(inputs):
                self.production_unit.set_state(ProductionUnitSTARTEDState)
                raise CannotProduce()
            self.progress += self.production_unit.rate
            if self.progress == 1:
                for input in inputs:
                    input.consume(spec)
                self.production_unit.outputs.extend(spec.output_materials)
                self.progress = 0
            self.production_time -= 1

class StopOperation(Operation):
    valid_state = [ProductionUnit.STARTED]
    def check(self):pass

    def perform(self):
        self.production_unit.set_state(ProductionUnitIDLEState)