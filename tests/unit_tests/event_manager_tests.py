from unittest import TestCase
from core.event import DayOfWorkIsOver, EventManager
from core.factory import Factory
from core.worker import Worker


class TestEventManager(TestCase):

    def raise_event(self, event, entity):
        def raise_event(self):
            raise event(entity)
        return raise_event

    def test_day_is_over(self):
        worker = Worker()
        Factory.run = self.raise_event(DayOfWorkIsOver, worker)
        event_manager = EventManager(Factory())

        event_manager.add_worker(worker)
        event_manager.run()
        self.assertEquals(event_manager.available_workers, [])

    def test_get_available_worker(self):
        event_manager = EventManager(Factory())
        self.assertEquals(event_manager.available_workers, [])

        event_manager.add_worker(Worker())
        self.assertEquals(len(event_manager.available_workers), 1)



