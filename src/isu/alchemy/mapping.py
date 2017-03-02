from zope.schema.interfaces import IFromUnicode
from isu.alchemy.interfaces import IColumn
from zope.component import adapter, getGlobalSiteManager
from zope.component import queryAdapter
import zope.schema
import sqlalchemy.types
import sqlalchemy
from zope.interface import implementer

DEFAULT = {
    zope.schema.Bool: sqlalchemy.types.Boolean,
    zope.schema.Int: sqlalchemy.types.Integer,
    zope.schema.Float: sqlalchemy.types.Float,
    #zope.schema.TextLine: sqlalchemy.types.Unicode,
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
    """Maps a zope.schema fields to a sqlalchemy one."""

    def __init__(self, **kwargs):
        self.mapping = DEFAULT
        opts = self.options = kwargs
        if "string-size" not in opts:
            opts["string-size"] = DEFAULT_STRING_SIZE

    def map(self, name, field, size=None, **kwargs):
        """Map the zope.schema field to a corrsponding
        Column of SQLAlchemy having 'name' as field name
        in its table.
        """
        alchtype = self.mapping.get(field.__class__, None)

        if alchtype is None:
            kwa = {}
            kwa.update(kwargs)
            return self.complex_map(
                size=size,
                field=field,
                name=name,
                options = kwa)
        if isinstance(alchtype, tuple):
            alchtype, args = alchtype
            alchtype = alchtype(**dict(args))
        if alchtype in [
                sqlalchemy.types.String,
                sqlalchemy.types.Unicode,
        ]:
            if size is None:
                size = self.options["string-size"]
            alchtype = alchtype(size)
        return sqlalchemy.Column(name, alchtype, **kwargs)

    def complex_map(self, name, field, size, options):
        # FIXME: Process everything in combination depending to
        # the set of implemented interfaces.
        # That wold be really COOL
        # Now it is exclusive.
        adapter = queryAdapter(field)
        if adapter is not None:
            column = sqlalchemy.Column(name=name,**options)
            adapter.convert(column)
            assert column.type_ is not None, "type must be defined"
            return column
        if zope.schema.interfaces.IChoice.implementedBy(field):
            return self.choice(kwa)
        if zope.schema.interfaces.ICollection.implementedBy(field):
            return self.collection(kwa)
        raise RuntimeError('cannot convert field')

## Adapter-oriented implementations
class ColumnAdapterBase(object):
    def __init__(self, field):
        self.field=field
        self.name=None
        self.field_name=None
        self.size=None

    def convert(self):
        """Run the conversion process."""
        raise RuntimeError("not implemented")

@implementer(IColumn)
@adapter(IFromUnicode)
class Adapter_IFromUnicodeToIColumn(ColumnAdapterBase):
    """Adapts unicode dtring fields
    to a storage Column of SQLAlchemy."""
    def convert(self, column):
        print(column.name)
        if self.size is not None:
            column.type_=sqlalchemy.types.String(self.size)
        else:
            column.type_=sqlalchemy.types.String
        return column

GSM=getGlobalSiteManager()
GSM.registerAdapter(Adapter_IFromUnicodeToIColumn)



