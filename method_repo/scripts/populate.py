import sys
from pyramid.paster import bootstrap

def main():
    env = bootstrap(sys.argv[1])
