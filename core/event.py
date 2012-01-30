import logging

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

class EventManager(object):

    def __init__(self, factory):
        self.factory = factory
        self.available_workers = []

    def initialize(self):
        for worker in self.available_workers:
            self.factory.add_worker(worker)
        self.factory.init_operations()

    def do_step(self):
        try:
            self.factory.do_step()
        except DayOfWorkIsOver, e:
            self.on_day_of_work_is_over(e.entity)

    def run(self, during):
        self.initialize()
        for i in range(during):
            logger.debug("###TIME### - %d" % i)
            self.do_step()

    def add_worker(self, worker):
        self.available_workers.append(worker)

    def on_day_of_work_is_over(self, worker):
        logger.info("On day is over")
        self.available_workers.remove(worker)

    

