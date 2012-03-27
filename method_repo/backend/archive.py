from repozitory.archive import Archive, log
from repozitory.schema import Base
from composite.alchemist.base import get_session

def hook(event):
    Base.metadata.bind = event.engine
    log.info("repozitory metadata bound")

class RepozitoryArchive(Archive):
    def __init__(self):
        super(RepozitoryArchive, self).__init__(None)

    @property
    def session(self):
        return get_session()

