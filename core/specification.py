import collections

class Specification(object):

    def __init__(self):
	self.constraints = []

    def add(self, constraint):
	self.constraints.append(constraint)

    def validate_all(self, inputs):
	if not inputs:
	    return False
	return all(constraint.validate(inputs) for constraint in self.constraints)

    def validate_any(self, inputs):
	if not inputs:
	    return False
	return any(constraint.validate(inputs) for constraint in self.constraints)

class InputConstraint(object):

    def __init__(self, type, quantity):
	self.type = type 
	self.quantity = quantity
 
    def validate(self, inputs):
        if not isinstance(inputs, collections.Iterable):
	    inputs = [inputs]
        for input in inputs:
	    if input.type == self.type and input.quantity >= self.quantity:
		return True
	return False	

class SkillConstraint(object):

    def __init__(self, skill_name):
	self.skill_name = skill_name


    def validate(self, workers):
 	return self.skill_name in worker.skills
