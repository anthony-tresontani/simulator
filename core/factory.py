import logging
from core import Runnable, Entity
from core.event import DayOfWorkIsOver

logger = logging.getLogger()

class Factory(Runnable, Entity):
    def __init__(self, name="", ID=None):
        Entity.__init__(self, ID)
        Runnable.__init__(self)
        self.workers = []
        self.available_workers = []
        self.production_units = []
        self.current_operations = []
        self.name = name

    def add_worker(self, worker):
        self.workers.append(worker)

    def add_production_unit(self, pu):
        self.production_units.append(pu)

    def init_operations(self):
        for machine in self.production_units:
            self.current_operations.append(machine.protocol.next())

        self.available_workers = self.workers[:]

    def execute_operation(self, operation):
        if self.available_workers:
            operation.worker = self.available_workers.pop()
        operation.run()
        if operation.is_operation_complete():
            self.current_operations.remove(operation)
            self.current_operations.append(operation.production_unit.protocol.next())
            self.available_workers.append(operation.worker)

    def run(self, during=1):
        self.init_operations()
        super(Factory, self).run(during)

    def do_step(self):
        for operation in self.current_operations:
            try:
                self.execute_operation(operation)
            except DayOfWorkIsOver, e:
                self.on_day_of_work_is_over(e.entity)
                self.execute_operation(operation)


    def on_day_of_work_is_over(self, worker):
        logger.info("-"*10)
        logger.info("On day is over")
        print self.available_workers
