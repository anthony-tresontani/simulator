import logging
from core import Runnable

logger = logging.getLogger()


class Event(Exception):
    def __init__(self, entity=None):
        self.entity = entity

class DayOfWorkIsOver(Event): pass
class StockIsFull(Event): pass
class NoWorkerToPerformAction(Event): pass

class IllegalStateToPerformAction(Exception): pass


class CannotProduce(Event): pass
class InvalidInputLoaded(CannotProduce): pass
class CannotPerformOperation(CannotProduce): pass



class Failure(object):
    def react(self, production_unit):
        from core.production_unit import ProductionUnitFAILUREState
        production_unit.set_state(ProductionUnitFAILUREState)


class Fix(object):
    def react(self, production_unit):
        from core.production_unit import ProductionUnitSTARTEDState
        production_unit.set_state(ProductionUnitSTARTEDState)