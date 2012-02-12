from core.factory import Factory
from yaml import load
from core.material import Material
from core.production_unit import ProductionUnit
from core.specification import Specification, MaterialInputConstraint
from core.worker import Worker

def create_materials(yaml):
    materials = {}
    for material in yaml.get("materials", []):
        materials[material["type"]] = {"type": material["type"], "price": material["price"]}
    return materials


def create_spec(materials, production_unit):
    spec = Specification()
    for input in production_unit.get("inputs", []):
        spec.add(MaterialInputConstraint(Material(type=input["input_type"], quantity=input["input_quantity"])))
    for output in production_unit.get("outputs", []):
        spec.add_output_material(Material(type=output["input_type"], quantity=output["input_quantity"],
                                          price=materials[output["input_type"]]["price"]))
    return spec


def get_factory(yaml_conf):
    yaml = load(yaml_conf)
    factory = Factory(name=yaml["name"])
    materials = create_materials(yaml)
    for production_unit in yaml["production_units"]:
        spec = create_spec(materials, production_unit)
        config = {}
        config["rate_by_minute"]= production_unit.get("rate", 1)
        factory.add_production_unit(ProductionUnit(spec=spec, config=config,  name=production_unit["name"]))

    for worker in yaml.get("workers", []):
        working_hour = worker.get("working_hour", 8) * 60
        factory.add_worker(Worker(working_hour=working_hour))
    return factory