import collections

class Specification(object):

    def __init__(self):
        self.constraints = []
        self.output_materials = []

    def add(self, constraint):
        self.constraints.append(constraint)

    def add_output_material(self, output_spec):
        self.output_materials.append(output_spec)

    def __str__(self):
        return "\n".join(map(lambda x: x.__str__(), self.constraints))

    def __repr__(self):
        return self.__str__()

    def validate_all(self, inputs):
        if not inputs:
            return False
        return all(constraint.validate(inputs) for constraint in self.constraints)

    def validate_any(self, inputs):
        if not inputs:
            return False
        return any(constraint.validate(inputs) for constraint in self.constraints)

class InputConstraint(object):

    def __str__(self):
        return str(self.__class__)

    def __repr__(self):
        return self.__str__()

class MaterialInputConstraint(InputConstraint):

    def __init__(self, material):
        self.material = material

    def __str__(self):
        return "Validate input is type of %s" % self.material.type

    def validate(self, inputs):
        if not isinstance(inputs, collections.Iterable):
            inputs = [inputs]
        for input in inputs:
            if input.type == self.material.type and input.quantity >= self.material.quantity:
                return True
        return False

class SkillConstraint(InputConstraint):

    def get_message(self):
        return "Worker does not have the skill %s" % self.skill_name

    def __str__(self):
        return "Validate worker has skill %s" % self.skill_name

    def __init__(self, skill_name):
        self.skill_name = skill_name

    def validate(self, worker):
        if not worker:
            return False
        return self.skill_name in worker.skills
