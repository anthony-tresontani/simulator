from output import Output


class NoLabourToPerformAction(Exception):pass


class IllegalStateToPerformAction(Exception):pass


class CannotProduce(Exception):pass


class InvalidInputLoaded(Exception):pass


class CannotPerformOperation(Exception):pass

class GoodProducer(object):
    IDLE, STARTED, PRODUCING, FAILURE = 0, 1, 2, 3

    def __init__(self, spec, config={}):
	self.worker = None
	self.inputs = None 
        self.outputs = []
	self.config = config
	self.spec = spec
	self.initialize()
        self.set_state(GoodProducerIDLEState)

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
 	operation.good_producer = self
	operation.check_all()
	operation.perform()


class Operation(object):
    def __init__(self, good_producer=None):
	self.good_producer = good_producer
	self.constraints = []

    def add_constraint(self, constraint):
	self.constraints.append(constraint)

    def check_all(self):
	self.check_valid_state()
	self.check()
	
    def check_valid_state(self):
	if not self.good_producer.get_state() in self.valide_state:
	    raise IllegalStateToPerformAction()


class LoadOperation(Operation):
    valide_state = [GoodProducer.IDLE, GoodProducer.STARTED]

    def __init__(self, inputs, good_producer=None):
	self.inputs = inputs
	super(LoadOperation, self).__init__(good_producer)

    def check(self):
	if not self.good_producer.spec.validate_any(inputs):
            raise InvalidInputLoaded()

    def perform(self, inputs):
	self.good_producer.inputs  = inputs


class StartOperation(Operation):
    valide_state = [GoodProducer.IDLE]
    def check(self):
	for constraint in self.constraints:
            if not constraint.validate(self.good_producer):
                raise CannotPerformOperation()

    def perform(self):
	for constraint in self.constraints:
	    if not constraint.validate(self.good_producer):
		raise CannotPerformOperation()
	self.good_producer.set_state(GoodProducerSTARTEDState)


class StopOperation(Operation):
    valide_state = [GoodProducer.STARTED]
    def check(self):pass

    def perform(self):
        self.good_producer.set_state(GoodProducerIDLEState)

class GoodProducerState(object):

    def __init__(self, good_producer):
	self.good_producer = good_producer

    def get_state(self):
	return self.STATUS

    def produce(self, minutes):
        raise IllegalStateToPerformAction("Action stop")


class GoodProducerIDLEState(GoodProducerState):
    STATUS = GoodProducer.IDLE

    def start(self):
        if not self.good_producer.worker:
            raise NoLabourToPerformAction()
        self.good_producer.start_operation.perform()


class GoodProducerSTARTEDState(GoodProducerState):
    STATUS = GoodProducer.STARTED

    def stop(self):
	if not self.good_producer.worker:
            raise NoLabourToPerformAction()
	self.good_producer.set_state(GoodProducerIDLEState)

    def produce(self, minutes):
        self.good_producer.set_state(GoodProducerPRODUCINGState)
	self.good_producer.produce(minutes)


class GoodProducerPRODUCINGState(GoodProducerState):
    STATUS = GoodProducer.PRODUCING

    def produce(self, production_time):
	progress = 0
        inputs = self.good_producer.inputs
        while production_time > 0:
	    if not self.good_producer.spec.validate_all(inputs):
                self.good_producer.set_state(GoodProducerSTARTEDState)
		raise CannotProduce()
	    progress += self.good_producer.rate
	    if progress == 1:
		inputs.quantity -= 1
            	self.good_producer.outputs.append(Output())
		progress = 0
	    production_time -= 1


class GoodProducerFAILUREState(GoodProducerState):
    STATUS = GoodProducer.FAILURE
