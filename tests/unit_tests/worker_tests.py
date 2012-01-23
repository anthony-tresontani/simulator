from unittest.case import TestCase
from core.event import Event
from core.worker import Worker

class TestWorker(TestCase):

    def test_working_hour(self):
        worker = Worker(working_hour=1)
        worker.add_unit_of_work()
        self.assertRaises(Event, worker.add_unit_of_work)