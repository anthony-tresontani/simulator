
class NoLabourToPerformAction(Exception):pass

class IllegalStateToPerformAction(Exception):pass

class NoInputToBeTransformed(Exception):pass


class GoodProducer(object):
    IDLE, STARTED, PRODUCING = 0, 1, 2

    def __init__(self):
	self.labour = None
	self.inputs = None
        self.set_state(GoodProducerIDLEState)

    def get_state(self):
	return self.state.get_state()

    def __getattr__(self, name):
	return getattr(self.state, name)

    def affect(self, labour):
	self.labour = labour

    def load(self, input):
	self.inputs  = input

    def set_state(self, state_class):
	self.state = state_class(self)


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
	if not self.good_producer.inputs:
	    raise NoInputToBeTransformed()
        self.good_producer.set_state(GoodProducerPRODUCINGState)

class GoodProducerPRODUCINGState(GoodProducerState):
    STATUS = GoodProducer.PRODUCING
