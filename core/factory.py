class Factory(object):

    def __init__(self):
        self.workers = []
        self.production_units = []

    def add_worker(self, worker):
        self.workers.append(worker)

    def add_production_unit(self, pu):
        self.production_units.append(pu)

    def run(self):
        pass