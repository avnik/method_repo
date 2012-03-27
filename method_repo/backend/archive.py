from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode
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

    def current(self, docid):
        return self.history(docid, only_current=True)[0]

class User(Base):
    """Dummy, use accounts/ownership to kotti or nanocms later"""
    __tablename__ = "nanocms_users"
    username = Column(Unicode, primary_key=True, nullable=True)
    password = Column(Unicode)

class Document(Base):
    __tablename__ = "methods_repo_documents"
    docid = Column(Integer, primary_key=True, nullable=False,
            autoincrement="ignore_fk")
    owner = Column(Unicode)
    vendor = Column(Unicode)
    title = Column(Unicode)
