import sys
from pyramid.paster import bootstrap
from composite.alchemist import get_base

def main():
    env = bootstrap(sys.argv[1])
    get_base().metadata.create_all()
    from method_repo.backend.archive import Base
    Base.metadata.create_all()

