from core.specification import MaterialInputConstraint

class Material(object):
    def __init__(self, type, quantity=1):
        self.type = type
        self.quantity = quantity

    def __str__(self):
        return "%d of %s" %(self.quantity, self.type)

    def __repr__(self):
        return self.__str__()

    def __add__(self, material):
        if material.type == self.type:
	    return Material(self.type, self.quantity + material.quantity)
        return self, material

    def __eq__(self, other):
        return self.type == other.type and self.quantity == other.quantity

    def consume(self, spec):
        for constraint in spec.constraints:
            if isinstance(constraint, MaterialInputConstraint) and constraint.material.type==self.type:
                self.quantity -= constraint.material.quantity
