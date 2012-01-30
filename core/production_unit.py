import collections
import logging
from core import Entity

from core.event import StockIsFull

logger = logging.getLogger()


class SignalDescriptor(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance._value

    def __set__(self, instance, value):
        instance._value = value

    def __delete__(self, instance):
        del(instance._value)

class Protocol(object):
    def __init__(self, machine):
        self._protocol_index = 0
        self.machine = machine
        self._protocol =  self.create_protocol()

    def create_protocol(self):
        from core.operation import StartOperation, LoadOperation, ProduceOperation
        protocol_list = [(StartOperation, {})]
        inputs = self.machine.spec.get_inputs() if self.machine.spec else []
        for input in inputs:
            protocol_list.append((LoadOperation, {"inputs":input}))
        protocol_list.append((ProduceOperation, {}))
        return protocol_list

    def next(self):
        if self._protocol_index < len(self._protocol):
            index = self._protocol_index
        else:
            index = (self._protocol_index - len(self._protocol)) % (len(self._protocol) -1) + 1
        protocol_tuple = self._protocol[index]
        protocol = protocol_tuple[0](production_unit=self.machine, **protocol_tuple[1])
        self._protocol_index += 1
        return protocol


class ProductionUnit(Entity):
    IDLE, STARTED, PRODUCING, FAILURE = 0, 1, 2, 3
    state = SignalDescriptor("state")

    def __init__(self, spec, config={}, input_stocking_zone=None, output_stocking_zone=None):
        super(ProductionUnit, self).__init__()
        self.inputs_stocking_zone = input_stocking_zone or StockingZone()
        self.outputs = []
        self.output_stocking_zone = output_stocking_zone or StockingZone()
        self.config = config
        self.spec = spec
        self.initialize()
        self.set_state(ProductionUnitIDLEState)
        self.protocol = Protocol(self)

    def initialize(self):
        self.rate = self.config.get("rate_by_minute", 1)
        self.input_types = self.config.get("input_types", None)

    def perform_next_operation(self, worker=None, during=1):
        operation = self.protocol.next()
        operation.worker = worker
        operation.run(during=during)

    @property
    def inputs(self):
        return self.inputs_stocking_zone

    def get_state(self):
        return self.state.get_state()

    def set_state(self, state_class):
        self.state = state_class(self)

    def load(self, input):
        self.inputs_stocking_zone.add_to_stock(input)

    def produce(self):
        for input in self.inputs_stocking_zone:
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
        if self.output_stocking_zone:
            try:
                self.output_stocking_zone.add_to_stock(outputs)
            except StockIsFull, e:
                e.entity = self
                raise e

    def add_output_stocking_zone(self, zone):
        if self.output_stocking_zone:
            self.output_stocking_zone.add_zone(self.output_stocking_zone)
        else:
            self.output_stocking_zone = zone

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

    def remove(self, element):
        if self.stock[element.type].quantity > element.quantity:
            self.stock[element.type] -= element.quantity
        else:
            del self.stock[element.type]

    def __iter__(self):
        return self.stock.values().__iter__()

    def get_flat_inputs(self):
        return self.stock.values()