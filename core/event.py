class Event(Exception):
    def __init__(self, entity=None):
        self.entity = entity

class DayOfWorkIsOver(Event): pass
class StockIsFull(Event): pass

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

    def run(self):
        try:
            self.factory.run()
        except DayOfWorkIsOver, e:
            self.on_day_of_work_is_over(e.entity)

    def add_worker(self, worker):
        self.available_workers.append(worker)

    def on_day_of_work_is_over(self, worker):
        self.available_workers.remove(worker)

    

