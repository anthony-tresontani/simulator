from core import Entity
from core.event import DayOfWorkIsOver

class Worker(Entity):

    def __init__(self, working_hour = 8 * 60):
        super(Worker, self).__init__()
        self.skills = []
        self.working_hour = working_hour
        self._hour_worked = 0

    @property
    def hour_worked(self):
        return self._hour_worked

    @hour_worked.setter
    def hour_worked(self, value):
        if value > self.working_hour:
            raise DayOfWorkIsOver(self)
        self._hour_worked = value

    def add_unit_of_work(self):
        self.hour_worked += 1
	
