from repozitory.archive import Archive, log
from repozitory.schema import Base
from composite.alchemist.base import get_session

def hook(event):
    Base.metadata.bind = event.engine
    log.info("repozitory metadata bound")

class RepozitoryArchive(Archive):
    @property
    def session(self):
        return get_session()

