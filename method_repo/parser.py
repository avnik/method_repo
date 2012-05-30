from six.moves import configparser
from six import text_type, binary_type
from codecs import EncodedFile

def snoop_encoding(fp):
    cp = configparser.ConfigParser()
    cp.readfp(fp)
    return cp.get("config", "encoding")

class ParsedDocumentProxy(object):
    def __init__(self, config, section):
        self.config = config
        self.section = section

    def __getitem__(self, key):
        return text_type(self.config.get(self.section, key), "utf-8")

    def __setitem__(self, key, value):
        self.config.set(self.section, key, value)

    def __contains__(self, key):
        return self.parser.has_option(self.section, key)

class ParsedDocument(object):
    def __init__(self, blob, encoding=None):
        if not encoding:
            encoding = snoop_encoding(blob)

        blob.seek(0)
        if not encoding == "utf-8":
            blob = EncodedFile(blob, "utf-8", encoding)

        self.parser = configparser.ConfigParser()
        self.parser.readfp(blob)
        self.encoding = encoding

    def __contains__(self, key):
        return self.parser.has_section(key)

    def __getitem__(self, key):
        return ParsedDocumentProxy(self.parser, key)
