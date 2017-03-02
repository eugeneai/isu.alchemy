from zope.interface import Interface
import zope.schema


class IStorable(Interface):
    """Mark a component as storable in a SQLAlchemy
    database.
    """


class IStorableRegistry(Interface):
    """Registry interface for all
    storable object Interface implementers.
    """


# class IStorageEngine(Interface):
#    """Marker interface for
#    storage engine of SQLAlchemy.
#    """

class IColumn(Interface):
    """Marker interface to define adapters
    for SQLAlchemy Columns
    """
