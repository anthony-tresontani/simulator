from core.material import Material
from core.production_unit import ProductionUnit, StockingZone
from core.specification import Specification, MaterialInputConstraint

def create_machine(material_type_input="input", material_type_output="output", stocking_zone_size=40, rate=1):
    spec = Specification()
    config = {'rate_by_minute': rate}
    spec.add(MaterialInputConstraint(Material(type=material_type_input, quantity=1)))
    spec.add_output_material(Material(type=material_type_output, quantity=1))
    machine = ProductionUnit(spec, config)
    stock_zone = StockingZone(size=stocking_zone_size)
    machine.add_stocking_zone(stock_zone)
    return machine, spec, stock_zone