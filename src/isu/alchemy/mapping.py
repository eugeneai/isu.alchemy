import zope.schema
import sqlalchemy.types
import sqlalchemy

DEFAULT = {
    zope.schema.Bool: sqlalchemy.types.Boolean,
    zope.schema.Int: sqlalchemy.types.Integer,
    zope.schema.TextLine: sqlalchemy.types.String
}

DEFAULT_STRING_SIZE = 256


class SchemaMapper(object):

    def __init__(self, **kwargs):
        self.mapping = DEFAULT
        opts = self.options = kwargs
        if "string-size" not in opts:
            opts["string-size"] = DEFAULT_STRING_SIZE

    def map(self, name, field, size=None, **kwargs):
        alchtype = self.mapping[field.__class__]
        if alchtype is sqlalchemy.types.String:
            if size is None:
                size = self.options["string-size"]
            alchtype = alchtype(size)
        return sqlalchemy.Column(name, alchtype, **kwargs)
