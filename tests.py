import unittest

from core.goodproducer import GoodProducer
from core.goodproducer import NoLabourToPerformAction, IllegalStateToPerformAction, NoInputToBeTransformed

from core.labour import Labour


class GoodProducerTest(unittest.TestCase):

    def setUp(self):
    	self.gp = GoodProducer()
        self.labour = Labour()

    def test_state_idle(self):
	self.assertEquals(self.gp.get_state(), GoodProducer.IDLE)

    def test_cannot_start_without_labour(self):
        self.assertRaises(NoLabourToPerformAction, self.gp.start)

    def test_start_with_labour(self):
	self.gp.affect(self.labour)
	self.gp.start()
	self.assertEquals(self.gp.get_state(), GoodProducer.STARTED)

    def test_stop_good_producer(self):
        self.gp.affect(self.labour)
 	self.gp.start()

        self.gp.stop()
        self.assertEquals(self.gp.get_state(), GoodProducer.IDLE)

    def test_illegal_state(self):
        self.assertRaises(IllegalStateToPerformAction, self.gp.stop)

    def test_produce_without_input(self):
	self.gp.affect(self.labour)
        self.gp.start()
        self.assertRaises(NoInputToBeTransformed, self.gp.produce, 1)
