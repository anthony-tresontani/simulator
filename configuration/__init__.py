from core.factory import Factory
from yaml import dump, load
from core.production_unit import ProductionUnit
from core.specification import Specification

def get_factory(yaml_conf):
    yaml = load(yaml_conf)
    factory = Factory(name=yaml["factory"])
    for production_unit in yaml["production_units"]:
        spec = Specification()
        config = {}
        config["rate_by_minute"]= production_unit.get("rate", 1)
        factory.add_production_unit(ProductionUnit(spec=spec, config=config))
    return factory