from nose.tools import set_trace

ref_counter = 1
entity_list = {}

class Entity(object):
    def __init__(self):
        global ref_counter
        self.reference = ref_counter
        ref_counter += 1
        entity_list[self.reference] = self

    @staticmethod
    def get_by_ref(ref_id):
        return entity_list.get(ref_id, None)
	
