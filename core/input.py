class Input(object):
    def __init__(self, type, quantity=1):
        self.type = type
        self.quantity = quantity

    def __str__(self):
        return "%d of %s" %(self.quantity, self.type)

    def __repr__(self):
        return self.__str__()
