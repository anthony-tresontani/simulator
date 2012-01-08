from output import Output
class NoLabourToPerformAction(Exception):pass

class IllegalStateToPerformAction(Exception):pass

class CannotProduce(Exception):pass

class InvalidInputLoaded(Exception):pass


class GoodProducer(object):
    IDLE, STARTED, PRODUCING = 0, 1, 2

    def __init__(self, spec, config={}):
	self.labour = None
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

    def affect(self, labour):
	self.labour = labour

    def load(self, inputs):
        operation = LoadOperation(self)
        operation.perform(inputs)

    def set_state(self, state_class):
	self.state = state_class(self)

    def get_outputs(self):
	return self.outputs

class Operation(object):
    def __init__(self, good_producer):
	self.good_producer = good_producer

class LoadOperation(Operation):
    def perform(self, inputs):
	if not self.good_producer.spec.validate_any(inputs):
	    raise InvalidInputLoaded()
	self.good_producer.inputs  = inputs


class GoodProducerState(object):

    def __init__(self, good_producer):
	self.good_producer = good_producer

    def get_state(self):
	return self.STATUS

    def start(self):
	raise IllegalStateToPerformAction("Action start")

    def stop(self):
	raise IllegalStateToPerformAction("Action stop")

    def produce(self, minutes):
        raise IllegalStateToPerformAction("Action stop")

class GoodProducerIDLEState(GoodProducerState):
    STATUS = GoodProducer.IDLE

    def start(self):
        if not self.good_producer.labour:
            raise NoLabourToPerformAction()
        self.good_producer.set_state(GoodProducerSTARTEDState)

class GoodProducerSTARTEDState(GoodProducerState):
    STATUS = GoodProducer.STARTED

    def stop(self):
	if not self.good_producer.labour:
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
