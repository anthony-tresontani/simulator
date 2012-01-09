import collections

class Specification(object):

    def __init__(self):
        self.constraints = []

    def add(self, constraint):
        self.constraints.append(constraint)

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

class Constraint(object):

    def __str__(self):
        return str(self.__class__)

    def __repr__(self):
        return self.__str__()

class InputConstraint(Constraint):

    def __init__(self, type, quantity):
        self.type = type
        self.quantity = quantity

    def __str__(self):
        return "Validate input is type of %s" % self.type

    def validate(self, inputs):
        if not isinstance(inputs, collections.Iterable):
            inputs = [inputs]
        for input in inputs:
            if input.type == self.type and input.quantity >= self.quantity:
                return True
        return False

class SkillConstraint(Constraint):

    def get_message(self):
        return "Worker does not have the skill %s" % self.skill_name

    def __str__(self):
        return "Validate worker has skill %s" % self.skill_name

    def __init__(self, skill_name):
        self.skill_name = skill_name

    def validate(self, production_unit):
        worker = production_unit.worker
        if not worker:
            return False
        return self.skill_name in worker.skills

