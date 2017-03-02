import unittest
from zope.interface import Interface, implementer
import zope.schema
from isu.alchemy.components import (
    AnInterfaceToISorableAdapter,
    Storage
)
from isu.alchemy.schema import determinants


class BasicTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        self.assertEqual(1 + 1, 2)

    def tearDown(self):
        pass


@determinants('code', 'group_code')
class IRefBookItem(Interface):

    code = zope.schema.Int(
        title=u"Code",
        description=u"The code of the item",
        readonly=True,
        required=True,
    )

    group_code = zope.schema.Int(
        title=u"Group Code",
        description=u"The code of the item group",
        readonly=True,
        required=True,
    )

    name = zope.schema.TextLine(
        title=u"Name",
        description=u"Name of the item",
        readonly=True,
        required=True
    )

    def test():
        """
        Just test method.
        """


@determinants('code')
@determinants('code', 'group_code', name='test')
class ICommondityItem(IRefBookItem):
    code = zope.schema.TextLine(
        title=u"Code",
        description=u"The code of the item",
        readonly=True,
        required=True,
    )
    price = zope.schema.Decimal(
        title=u"Price",
        description=u"The price of the item",
        required=True
    )
    b = zope.schema.Bool(
        title="ABool"
    )
    i = zope.schema.Int(
        title="ABool"
    )
    f = zope.schema.Float(
        title="ABool"
    )
    t = zope.schema.Text(
        title="ABool"
    )


class TestSimpleObjectStorage:

    def setUp(self):

        @implementer(IRefBookItem)
        class RefBookItem(object):

            def __init__(self, code, name):
                self.code = code
                self.name = name

        @implementer(ICommondityItem)
        class Commondity(object):

            def __init__(self, code, name):
                self.code = code
                self.name = name

        self.storage = Storage('sqlite:///:memory:', echo=True)
        self.storage.register_class(RefBookItem)
        self.storage.register_class(Commondity)
        self.storage.initialize()
        self.rbi = RefBookItem(1, "Bread")
        self.com = Commondity(1, "Table")
        self.storage.commit()

    def test_interface(self):
        assert IRefBookItem.providedBy(self.rbi)

    def test_storage_of_rbi(self):
        adapted = AnInterfaceToISorableAdapter(self.rbi)
        self.storage.store(self.rbi)
