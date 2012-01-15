from core.entity import Entity

class Worker(Entity):
    def __init__(self):
	super(Worker, self).__init__()
        self.skills = []
	
