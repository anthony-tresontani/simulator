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


class ProductionUnitIDLEState(ProductionUnitState):
    STATUS = ProductionUnit.IDLE


class ProductionUnitSTARTEDState(ProductionUnitState):
    STATUS = ProductionUnit.STARTED


class ProductionUnitPRODUCINGState(ProductionUnitState):
    STATUS = ProductionUnit.PRODUCING


class ProductionUnitFAILUREState(ProductionUnitState):
    STATUS = ProductionUnit.FAILURE
