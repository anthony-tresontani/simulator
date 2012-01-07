import unittest

from core.goodproducer import GoodProducer
from core.goodproducer import NoLabourToPerformAction, IllegalStateToPerformAction, NoInputToBeTransformed, InvalidInputLoaded

from core.input import Input
from core.labour import Labour


class GoodProducerTest(unittest.TestCase):

    def setUp(self):
	config = {"input_types":["yarn"]}
    	self.gp = GoodProducer(config)
        self.labour = Labour()
        self.inputs = Input("yarn")

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

    def test_produce_with_input(self):
	self.gp.affect(self.labour)
	self.gp.load(self.inputs)
	
	self.gp.start()
	self.gp.produce(1)
        self.assertEquals(self.gp.get_state(), GoodProducer.PRODUCING)

    def test_production_output(self):
        self.gp.affect(self.labour)
        self.gp.load(self.inputs)
            
        self.gp.start()
        self.gp.produce(1)	
	self.assertEquals(len(self.gp.get_outputs()), 1) 

    def test_slower_machine(self):
	config = {'rate_by_minute': 0.5,
		  "input_types":["yarn"],}
	slower_gp = GoodProducer(config)

        slower_gp.affect(self.labour)
        slower_gp.load(self.inputs)
                
        slower_gp.start()
        slower_gp.produce(2)    
        self.assertEquals(len(slower_gp.get_outputs()), 1)

    def test_invalid_input(self):
	input = Input("rocks")
	
	self.assertRaises(InvalidInputLoaded, self.gp.load, input)

    
    def test_out_of_stock(self):
	self.assertTrue(False)


    def test_multiple_inputs(self):
	self.assertTrue(False)

    
    def test_complete_failure(self):
	 self.assertTrue(False)

    def test_partial_failure(self):
        # slow down the machine
	self.assertTrue(False)
