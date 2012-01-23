import collections
import logging

from core.entity import Entity

logger = logging.getLogger()

class NoWorkerToPerformAction(Exception): pass


class IllegalStateToPerformAction(Exception): pass


class Event(Exception): pass


class CannotProduce(Event): pass


class InvalidInputLoaded(Event): pass


class CannotPerformOperation(Event): pass


class StockIsFull(Event): pass


class SignalDescriptor(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance._value

    def __set__(self, instance, value):
        if hasattr(instance, self.name):
            print "Was %s" % getattr(instance, self.name)
        instance._value = value
        print "Is %s" % instance._value

    def __delete__(self, instance):
        del(instance._value)

class ProductionUnit(Entity):
    IDLE, STARTED, PRODUCING, FAILURE = 0, 1, 2, 3
    state = SignalDescriptor("state")

    def __init__(self, spec, config={}):
        super(ProductionUnit, self).__init__()
        self.inputs = []
        self.outputs = []
        self.stocking_zone = None
        self.config = config
        self.spec = spec
        self.initialize()
        self.set_state(ProductionUnitIDLEState)

    def initialize(self):
        self.rate = self.config.get("rate_by_minute", 1)
        self.input_types = self.config.get("input_types", None)

    def get_state(self):
        return self.state.get_state()

    def set_state(self, state_class):
        self.state = state_class(self)

    def load(self, input):
        self.inputs.append(input)

    def produce(self):
        for input in self.inputs:
            input.consume(self.spec)
            if not input.quantity:
                self.inputs.remove(input)
        self.set_output(self.spec.output_materials)

    def get_outputs(self):
        return self.outputs

    def add_event(self, event):
        event.react(self)

    def set_output(self, outputs):
        self.outputs = outputs
        if self.stocking_zone:
            self.stocking_zone.add_to_stock(outputs)

    def add_stocking_zone(self, zone):
        if self.stocking_zone:
            self.stocking_zone.add_zone(self.stocking_zone)
        else:
            self.stocking_zone = zone

    def stop(self):
        self.set_state(ProductionUnitIDLEState)

    def start(self):
        self.set_state(ProductionUnitSTARTEDState)


class ProductionUnitState(object):
    def __init__(self, production_unit):
        self.production_unit = production_unit

    def get_state(self):
        return self.STATUS


class ProductionUnitIDLEState(ProductionUnitState):
    STATUS = ProductionUnit.IDLE


class ProductionUnitSTARTEDState(ProductionUnitState):
    STATUS = ProductionUnit.STARTED


class ProductionUnitPRODUCINGState(ProductionUnitState):
    STATUS = ProductionUnit.PRODUCING


class ProductionUnitFAILUREState(ProductionUnitState):
    STATUS = ProductionUnit.FAILURE


class StockingZone():
    def __init__(self, size=None):
        self.stock = {}
        self.size = size # None means unlimited

    def count(self):
        return sum([material.quantity for material in self.stock.values()])

    def add_to_stock(self, elements):
        if self.size and self.count() >= self.size:
            raise StockIsFull()
        if not isinstance(elements, collections.Iterable):
            elements = [elements]
        for element in elements:
            if not element.quantity:
                logger.warning("Try to add empty element of type %s" % element.type)
            if element.type not in self.stock:
                self.stock[element.type] = element
            else:
                self.stock[element.type] += element
        logger.debug("Add elements to the stock. Stock(%d/%s)", self.count(), self.size if self.size else "unlimited")

    def add_zone(self, zone):
        pass
