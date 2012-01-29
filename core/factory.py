import logging

logger = logging.getLogger()

class Factory(object):
    def __init__(self):
        self.workers = []
        self.production_units = []
        self.current_operations = []

    def add_worker(self, worker):
        self.workers.append(worker)

    def add_production_unit(self, pu):
        self.production_units.append(pu)

    def init_operations(self):
        for machine in self.production_units:
            self.current_operations.append(machine.protocol.next())

        self.available_worker = self.workers[:]

    def do_step(self):
        for operation in self.current_operations:
            operation.worker = self.available_worker.pop()
            operation.perform()
            if operation.is_operation_complete():
                self.current_operations.remove(operation)
                self.current_operations.append(operation.production_unit.protocol.next())
                self.available_worker.append(operation.worker)

    def run(self, during):
        for i in range(during):
            self.do_step()