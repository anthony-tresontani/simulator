from core import Entity

class EntityNotFound(Exception):pass

class Report(object):
    def get_factory_data(self, ID_factory):
        factory = Entity.get_by_ref(ID_factory)
        values = {}
        values["Current time"] = factory.time
        values["number of production unit"] = len(factory.production_units)
        values["number of workers"] = len(factory.workers)
        return values

    def get_production_unit_data(self, factory_ID, name):
        factory = Entity.get_by_ref(factory_ID)
        values = {}
        production_unit = None
        for pu in factory.production_units:
            if pu.name == name:
                production_unit = pu
                break
        if not production_unit:
            raise EntityNotFound("No production unit found with name %s" % name)
        values["produce"] = [material.type for material in production_unit.spec.output_materials]
        values["units_produced"] = production_unit.unit_produced
        values["value_produced"] = sum([material.price * production_unit.unit_produced for material in production_unit.spec.output_materials])
        return values