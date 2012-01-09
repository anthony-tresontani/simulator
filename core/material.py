from core.specification import MaterialInputConstraint

class Material(object):
    def __init__(self, type, quantity=1):
        self.type = type
        self.quantity = quantity

    def __str__(self):
        return "%d of %s" %(self.quantity, self.type)

    def __repr__(self):
        return self.__str__()

    def consume(self, spec):
        for constraint in spec.constraints:
            print constraint
            if isinstance(constraint, MaterialInputConstraint) and constraint.type==self.type:
                self.quantity -= constraint.quantity
