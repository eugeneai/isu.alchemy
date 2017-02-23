import zope.schema
import sqlalchemy.types
import sqlalchemy

DEFAULT = {
    zope.schema.Bool: sqlalchemy.types.Boolean,
    zope.schema.Int: sqlalchemy.types.Integer,
    zope.schema.Float: sqlalchemy.types.Float,
    zope.schema.TextLine: sqlalchemy.types.Unicode,
    # FIXME: How To differ from Unicode?
    zope.schema.Text: sqlalchemy.types.UnicodeText,
    zope.schema.Bytes: sqlalchemy.types.String,
    zope.schema.BytesLine: sqlalchemy.types.String,
    zope.schema.ASCII: sqlalchemy.types.String,
    zope.schema.ASCIILine: sqlalchemy.types.String,
    zope.schema.SourceText: sqlalchemy.types.String,
    zope.schema.URI: sqlalchemy.types.String,
    zope.schema.DottedName: sqlalchemy.types.String,
    zope.schema.Id: sqlalchemy.types.String,

    zope.schema.Decimal: sqlalchemy.types.Numeric,  # FIXME: PASS parameters


    zope.schema.Datetime: (sqlalchemy.types.DateTime, ("timezone", True)),
    zope.schema.Date: (sqlalchemy.types.Date, ("timezone", True)),
    zope.schema.Time: (sqlalchemy.types.Time, ("timezone", True)),

}

# InterfaceField
# Choice -> Enum or Relation
# List,Tuple,Set,FrozenSet,Object, Dict -> ? relation


DEFAULT_STRING_SIZE = 256


class SchemaMapper(object):

    def __init__(self, **kwargs):
        self.mapping = DEFAULT
        opts = self.options = kwargs
        if "string-size" not in opts:
            opts["string-size"] = DEFAULT_STRING_SIZE

    def map(self, name, field, size=None, **kwargs):
        alchtype = self.mapping[field.__class__]
        if isinstance(alchtype, tuple):
            alchtype, args = alchtype
            alchtype = alchtype(**dict(args))
        if alchtype in [
                sqlalchemy.types.String,
                # sqlalchemy.types.Text,
                sqlalchemy.types.Unicode,
                # sqlalchemy.types.UnicodeText,
        ]:
            if size is None:
                size = self.options["string-size"]
            alchtype = alchtype(size)
        return sqlalchemy.Column(name, alchtype, **kwargs)
