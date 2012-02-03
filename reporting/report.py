class Report(object):

    def __init__(self, factory):
        self.factory = factory

    def get_data(self):
        values = {}
        values["number of production unit"] = len(self.factory.production_units)
        values["number of workers"] = len(self.factory.workers)
        return values