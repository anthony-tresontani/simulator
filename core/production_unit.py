from output import Output


class NoWorkerToPerformAction(Exception): pass


class IllegalStateToPerformAction(Exception): pass


class CannotProduce(Exception): pass


class InvalidInputLoaded(Exception): pass


class CannotPerformOperation(Exception): pass


class ProductionUnit(object):
    IDLE, STARTED, PRODUCING, FAILURE = 0, 1, 2, 3

    def __init__(self, spec, config={}):
        self.worker = None
        self.inputs = None
        self.outputs = []
        self.config = config
        self.spec = spec
        self.initialize()
        self.set_state(ProductionUnitIDLEState)

    def initialize(self):
        self.rate = self.config.get("rate_by_minute", 1)
        self.input_types = self.config.get("input_types", None)

    def get_state(self):
        return self.state.get_state()

    def __getattr__(self, name):
        return getattr(self.state, name)


    def affect(self, worker):
        self.worker = worker

    def set_state(self, state_class):
        print "Change state to %s" % state_class
        self.state = state_class(self)

    def get_outputs(self):
        return self.outputs

    def add_event(self, event):
        event.react(self)

    def perform_operation(self, operation):
        operation.production_unit    = self
        operation.check_all()
        operation.perform()


class ProductionUnitState(object):
    def __init__(self, production_unit):
        self.production_unit = production_unit

    def get_state(self):
        return self.STATUS

    def produce(self, minutes):
        raise IllegalStateToPerformAction("Produce")


class ProductionUnitIDLEState(ProductionUnitState):
    STATUS = ProductionUnit.IDLE


class ProductionUnitSTARTEDState(ProductionUnitState):
    STATUS = ProductionUnit.STARTED

    def stop(self):
        if not self.production_unit.worker:
            raise NoWorkerToPerformAction()
        self.production_unit.set_state(ProductionUnitIDLEState)

    def produce(self, minutes):
        self.production_unit.set_state(ProductionUnitPRODUCINGState)
        self.production_unit.produce(minutes)


class ProductionUnitPRODUCINGState(ProductionUnitState):
    STATUS = ProductionUnit.PRODUCING

    def produce(self, production_time):
        progress = 0
        inputs = self.production_unit.inputs
        while production_time > 0:
            if not self.production_unit.spec.validate_all(inputs):
                self.production_unit.set_state(ProductionUnitSTARTEDState)
                raise CannotProduce()
            progress += self.production_unit.rate
            if progress == 1:
                inputs.quantity -= 1
                self.production_unit.outputs.append(Output())
                progress = 0
            production_time -= 1


class ProductionUnitFAILUREState(ProductionUnitState):
    STATUS = ProductionUnit.FAILURE
