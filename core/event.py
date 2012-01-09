from core.production_unit import ProductionUnitFAILUREState, ProductionUnitSTARTEDState

class Failure(object):
    def react(self, production_unit):
	production_unit.set_state(ProductionUnitFAILUREState)

class Fix(object):
    def react(self, production_unit):
        production_unit.set_state(ProductionUnitSTARTEDState)
