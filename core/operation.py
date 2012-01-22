import copy
import logging

from core.production_unit import IllegalStateToPerformAction, ProductionUnit, NoWorkerToPerformAction,\
    InvalidInputLoaded, CannotPerformOperation, ProductionUnitSTARTEDState, ProductionUnitIDLEState,\
    CannotProduce, ProductionUnitPRODUCINGState

logger = logging.getLogger()


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


class Operation(object):
    def __init__(self, production_unit=None, time_to_perform=1):
        self.production_unit = production_unit
        self.constraints = []
        self.time_to_perform = time_to_perform
        self.elapsed_time = 0
        self.progress = 0.0

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def check_all(self, worker):
        self.check_valid_state()
        if hasattr(self, "constraints"):
            self.check_constraints(worker)
        if hasattr(self, "static_constraints"):
            self.check_static_constraints(worker)
        if hasattr(self, "check"):
            self.check(worker)

    def check_valid_state(self):
        if hasattr(self, "valid_state") and not self.production_unit.get_state() in self.valid_state:
            raise IllegalStateToPerformAction(
                "Action %s cannot be perform while in state %s" % (self, self.production_unit.state))

    def check_constraints(self, worker):
        for constraint in self.constraints:
            if not constraint.validate(worker):
                raise CannotPerformOperation(constraint.get_message())

    def check_static_constraints(self, worker):
        for constraint in self.static_constraints:
            constraint(self).validate(worker)

    def perform(self, worker, during=1):
        self.check_all(worker)
        for i in range(during):
            logger.debug("###TIME### - %d" % i)
            self.do_step(worker)

    def do_step(self, worker):
        if self.is_operation_complete():
            self.progress = 0

        if self.operation_ready_to_be_performed():
            self._do_step(worker)
            self.progress += self.get_progress_step()

        if self.is_operation_complete():
            self.on_operation_complete()

    def on_operation_complete(self):
        pass

    def get_progress_step(self):
        return 1.0 / self.time_to_perform

    def operation_ready_to_be_performed(self):
        return True

    def is_operation_complete(self):
        return self.progress == 1

    def _do_step(self, worker):
        pass

class LoadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED, ProductionUnit.PRODUCING]
    static_constraints = [HasWorkerConstraint, InputValidForSpecConstraint]

    def __init__(self, inputs, *args, **kwargs):
        self.inputs = inputs
        super(LoadOperation, self).__init__(*args, **kwargs)

    def check(self, worker=None):
        if not worker:
            raise NoWorkerToPerformAction()
        if not self.production_unit.spec.validate_any(self.inputs):
            raise InvalidInputLoaded()

    def _do_step(self, worker):
        input = copy.copy(self.inputs)
        input.quantity = self.inputs.quantity / self.time_to_perform
        self.production_unit.inputs.append(input)


class AllInOneLoadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]

    def __init__(self, inputs, *args, **kwargs):
        self.inputs = inputs
        super(AllInOneLoadOperation, self).__init__(*args, **kwargs)

    def check(self, worker=None):
        if not worker:
            raise NoWorkerToPerformAction()
        if not self.production_unit.spec.validate_any(self.inputs):
            raise InvalidInputLoaded()

    def on_operation_complete(self):
        input = copy.copy(self.inputs)
        self.production_unit.inputs.append(input)


class UnloadOperation(Operation):
    valid_state = [ProductionUnit.IDLE, ProductionUnit.STARTED]

    def __init__(self, quantity, zone, *args, **kwargs):
        self.quantity = quantity
        self.zone = zone
        super(UnloadOperation, self).__init__(*args, **kwargs)

    def _do_step(self, worker):
        self.done = self.quantity * self.progress
        self.zone.add_to_stock(self.production_unit.stocking_zone.stock.popitem()[1])

    def operation_ready_to_be_performed(self):
        return bool(self.production_unit.stocking_zone.stock)

class StartOperation(Operation):
    valid_state = [ProductionUnit.IDLE]

    def _do_step(self, *args, **kwargs):
        self.production_unit.set_state(ProductionUnitSTARTEDState)


class ProduceOperation(Operation):
    valid_state = [ProductionUnit.STARTED, ProductionUnit.PRODUCING]

    def get_progress_step(self):
        return self.production_unit.rate

    def _do_step(self, worker):
        if not self.progress:
            self.progress += self.get_progress_step()
        if not self.production_unit.get_state() == ProductionUnit.PRODUCING:
            self.production_unit.set_state(ProductionUnitPRODUCINGState)

        inputs = self.production_unit.inputs
        spec = self.production_unit.spec
        if not spec.validate_all(self.production_unit.inputs):
            self.production_unit.set_state(ProductionUnitSTARTEDState)
            raise CannotProduce("Inputs %s does not match constraints %s" % (inputs, spec))
        if self.progress == 1:
            for input in self.production_unit.inputs:
                input.consume(spec)
                if not input.quantity:
                    self.production_unit.inputs.remove(input)
            self.production_unit.set_output(self.production_unit.spec.output_materials)
            self.progress = 0

    def on_operation_complete(self):
        logger.debug("Produce has completed a product")

    def get_elapsed_time(self):
        return self.elapsed_time

    def is_operation_complete(self):
        return not bool(self.production_unit.inputs)


class StopOperation(Operation):
    valid_state = [ProductionUnit.STARTED]

    def _do_step(self, worker):
        self.production_unit.set_state(ProductionUnitIDLEState)


class Process(Operation):
    def __init__(self, production_unit, operations):
        super(Process, self).__init__(production_unit=production_unit)
        self.operations = operations
        self.queue = self.operations[:]
        self.current = self.queue.pop(0)

    def _do_step(self, worker):
        logger.debug("Process: Current operation: %s" % self.current)
        self.current.do_step(worker)
        if self.current.is_operation_complete():
            if not self.queue:
                self.queue.extend(self.operations[:])
            self.current = self.queue.pop(0)


class ParallelProcess(Operation):
    def __init__(self, process_list):
        super(ParallelProcess, self).__init__(      )
        self.processes = process_list

    def _do_step(self, worker):
        for process in self.processes:
            logger.debug("Running parallel process %s" % process)
            process.do_step(worker)
