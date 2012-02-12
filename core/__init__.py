ref_counter = 1
entity_list = {}

class AlreadyUsedID(Exception):pass

class Entity(object):
    def __init__(self, ID=None):
        global ref_counter
        self.reference = ref_counter
        ref_counter += 1
        entity_list[self.reference] = self

    @staticmethod
    def get_by_ref(ref_id):
        return entity_list.get(ref_id, None)

class Runnable(object):

    def __init__(self):
        self.time = 0

    def run(self, i=1):
        for i in range(i):
            self.do_step()
            self.time += 1