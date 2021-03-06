from zope.schema.interfaces import IFromUnicode, IBool, IInt
from zope.schema.interfaces import ITextLine, IFloat, IText
from isu.alchemy.interfaces import IColumn
from zope.component import adapter, getGlobalSiteManager
from zope.component import queryAdapter
import zope.schema
import sqlalchemy.types
import sqlalchemy
from zope.interface import implementer, Interface, providedBy

DEFAULT = {
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

    def __init__(self, relations, **kwargs):
        self.mapping = DEFAULT
        self.relations = relations
        opts = self.options = kwargs
        if "string-size" not in opts:
            opts["string-size"] = DEFAULT_STRING_SIZE

    def map(self, name, field, size=None, **kwargs):
        """Map the zope.schema field to a corrsponding
        Column of SQLAlchemy having 'name' as field name
        in its table.
        """
        #print(name, field)
        # print(list(providedBy(field)))
        field_class = field.__class__
        alchtype = self.mapping.get(field_class, None)
        adapter = queryAdapter(field)
        if adapter is not None:
            kw = {}
            kw.update(kwargs)
            kw["__relations__"] = self.relations
            type_ = adapter.convert(name=name,
                                    size=size,
                                    options=kw)
            kw = {k: v for k, v in kw.items() if not k.startswith("__")}
            if type_ is not None:
                return sqlalchemy.Column(name, type_, **kw)
            else:
                return None
        elif alchtype is None:
            kwa = {}
            kwa.update(kwargs)
            return self.complex_map(
                size=size,
                field=field,
                name=name,
                options=kwa)
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
        kw = {k: v for k, v in kwargs.items() if not k.startswith("__")}
        return sqlalchemy.Column(name, alchtype, **kw)

    def complex_map(self, name, field, size, options):
        # FIXME: Process everything in combination depending to
        # the set of implemented interfaces.
        # That wold be really COOL
        # Now it is exclusive.
        if zope.schema.interfaces.IChoice.providedBy(field):
            return self.choice(size=size,
                               field=field,
                               name=name,
                               options=options)
        raise RuntimeError('cannot convert field')

# Adapter-oriented implementations


@implementer(IColumn)
class ColumnAdapterBase(object):

    def __init__(self, field):
        self.field = field
        self.name = None

    def convert(self):
        """Run the conversion process."""
        raise RuntimeError("not implemented")


@adapter(ITextLine)
class Adapter_IFromUnicodeToIColumn(ColumnAdapterBase):
    """Adapts unicode dtring fields
    to a storage Column of SQLAlchemy."""

    def convert(self, name, size=None, options=None):
        if size is not None:
            type_ = sqlalchemy.types.String(self.size)
        else:
            type_ = sqlalchemy.types.String
        return type_


@adapter(IText)
class Adapter_ITextToIColumn(ColumnAdapterBase):
    """Adapts unicode dtring fields
    to a storage Column of SQLAlchemy."""

    def convert(self, name, size=None, options=None):
        if size is not None:
            type_ = sqlalchemy.types.Text(self.size)
        else:
            type_ = sqlalchemy.types.Text
        return type_


@adapter(IBool)
class Adapter_IBoolToIColumn(ColumnAdapterBase):
    """Adapts Boolean fields."""

    def convert(self, name, size=None, options=None):
        return sqlalchemy.types.Boolean


@adapter(IInt)
class Adapter_IIntToIColumn(ColumnAdapterBase):
    """Adapts Boolean fields."""

    def convert(self, name, size=None, options=None):
        return sqlalchemy.types.Integer


@adapter(IFloat)
class Adapter_IFloatToIColumn(ColumnAdapterBase):
    """Adapts Boolean fields."""

    def convert(self, name, size=None, options=None):
        return sqlalchemy.types.Float


#@adapter(ICollection)
#@adapter(IChoice)
class Adapter_ReferenceToIColumn(ColumnAdapterBase):
    def convert(self, name, size=None, options=None):
        relations = options["__relations__"]
        cls = options["__cls__"]
        relations[(cls, name)] = self.field
        return None


GSM = getGlobalSiteManager()
GSM.registerAdapter(Adapter_ITextToIColumn)
GSM.registerAdapter(Adapter_IBoolToIColumn)
GSM.registerAdapter(Adapter_IIntToIColumn)
GSM.registerAdapter(Adapter_IFloatToIColumn)
GSM.registerAdapter(Adapter_IFromUnicodeToIColumn)

GSM.registerAdapter(Adapter_ReferenceToIColumn,
                    (zope.schema.interfaces.ICollection,))
GSM.registerAdapter(Adapter_ReferenceToIColumn,
                    (zope.schema.interfaces.IChoice,))
