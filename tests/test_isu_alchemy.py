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


@determinants("id")
class IVocabularyItem(Interface):
    id = zope.schema.Int(
        title="Code",
        description="The code of the Vocabulary item",
        required=True
    )
    name = zope.schema.TextLine(
        title="Name",
        description="Name of the Vocabulary item",
        required=True
    )


#@determinants("id")
class IEmployee(IVocabularyItem):
    """Defines schema for Employees"""
    contractor = zope.schema.Choice(
        title="Contractor",
        description="The Contractor that hired the Employee",
        vocabulary="contractors"
    )


#@determinants("id")
class IContractor(IVocabularyItem):
    employees = zope.schema.List(
        title="Employees",
        description="The list of Employees of the Contractor",
        value_type=zope.schema.Object(
            title="Employees",
            description="An Employee element",
            schema=IEmployee
        )
    )


@implementer(IVocabularyItem)
class VocabularyItem(object):
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


@implementer(IEmployee)
class Employee(VocabularyItem):
    def __init__(self, id=None, name=None, contractor=None):
        super(Contractor, self).init(id=id, name=name)
        self.contractor = contractor


@implementer(IContractor)
class Contractor(VocabularyItem):
    def __init__(self, id=None, name=None, employees=None):
        super(Contractor, self).init(id=id, name=name)
        if employees is None:
            employees = []
        self.employees = employees


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


class TestOneToManyRelation(object):
    def setUp(self):
        st = self.storage = Storage("sqlite:///:memory:", echo=True)
        st.register_class(Employee)
        st.register_class(Contractor)
        print("-" * 30)
        print(st.relations)
        print("-" * 30)
        st.initialize()

    def test_db_creation(self):
        assert self.storage
