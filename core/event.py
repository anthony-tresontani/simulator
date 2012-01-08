from core.goodproducer import GoodProducerFAILUREState, GoodProducerSTARTEDState

class Failure(object):
    def react(self, production_unit):
	production_unit.set_state(GoodProducerFAILUREState)

class Fix(object):
    def react(self, production_unit):
        production_unit.set_state(GoodProducerSTARTEDState)
