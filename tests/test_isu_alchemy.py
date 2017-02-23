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
        pass


class TestSimpleObjectStorage:

    def setUp(self):

        @implementer(IRefBookItem)
        class RefBookItem(object):

            def __init__(self, code, name):
                self.code = code
                self.name = name

        self.storage = Storage('sqlite:///:memory:', echo=True)
        self.storage.register_class(RefBookItem)
        self.storage.initialize()
        self.rbi = RefBookItem(1, "Bread")
        self.storage.commit()

    def test_interface(self):
        assert IRefBookItem.providedBy(self.rbi)

    def test_storage_of_rbi(self):
        adapted = AnInterfaceToISorableAdapter(self.rbi)
        self.storage.store(self.rbi)
