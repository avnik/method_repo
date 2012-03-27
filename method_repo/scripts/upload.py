import sys
from pyramid.paster import bootstrap
from ..resources import MethodFolder

def main():
    env = bootstrap(sys.argv[1])
    folder = MethodFolder(env['request'])
    folder.upload(open(sys.argv[2], 'rb'))
