from isu.alchemy.interfaces import IStorable
from zope.interface import implementer, Interface, implementedBy
from zope.component import adapter, getGlobalSiteManager
import zope.schema
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey

from isu.enterprise.interfaces import IStorage
import isu.alchemy.mapping as alcmap
import collections


@implementer(IStorable)
@adapter(Interface)
class AdapterBase(object):
    """
    A bases class for creating stable adapters
    """

    def __init__(self, object):
        self.object = object


class AnInterfaceToISorableAdapter(AdapterBase):
    """
    The implementer class for storing objects in a
    general way.
    """


@implementer(IStorage)
class Storage(object):

    def __init__(self, *args, prefix='', **kwargs):
        self.engine = sqlalchemy.create_engine(*args, **kwargs)
        session = sqlalchemy.orm.sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()
        self.metadata = MetaData()
        self.type_mapper = alcmap.SchemaMapper()  # FIXME make it an utility
        self.registry = {}
        self.prefix = prefix

    def initialize(self):
        self.metadata.create_all(self.engine)

    def store(self, object):
        if isinstance(object, tuple) or isinstance(object, list):
            self.session.add_all(object)
        else:
            self.session.add(object)
        return object

    def commit(self):
        self.session.commit()

    def register_class(self, cls, tablename=None):
        # FIXME better ask mapper itself
        if cls in self.registry:
            return cls
        assert Interface.implementedBy(cls)
        table = self._add_metadata_for(cls, tablename=tablename)
        self.registry[cls] = table

    def _interfaces(self, cls):
        ifaces = implementedBy(cls)
        for iface in ifaces:
            yield iface

    def _fields(self, cls):
        """Enumerate all fields of implemented interface
        in appearance order.
        """
        for iface in self._interfaces(cls):
            fields = zope.schema.getFieldsInOrder(iface)
            for name, field in fields:
                yield name, field, iface

    def _add_metadata_for(self, cls, tablename=None):
        if tablename is None:
            tablename = cls.__name__

        tablename = self.prefix + tablename

        determinants = collections.OrderedDict()
        for iface in self._interfaces(cls):
            if hasattr(iface, "__sql_determinants__"):
                determinants.update(iface.__sql_determinants__)

        def_det = list(determinants.values())[0]

        columns = []
        # FIXME Suppose the first field to be key.
        # May be add some adapter engine defining set of
        # attributes describing key

        for name, field, iface in self._fields(cls):
            columns.append(self.type_mapper.map(
                name, field, primary_key=name in def_det))

        table = Table(tablename, self.metadata,
                      *columns
                      )
        sqlalchemy.orm.mapper(cls, table)
        # gsm = getGlobalSiteManager()
        # gsm.registerUtility(...)
