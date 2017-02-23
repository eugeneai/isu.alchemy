import collections
#from zope.component import getUtility
#from isu.enterprise import IDeterminantRegistry


# class DeterminantRegistry(object):

#     def __init__(self):
#         self.interfaces = collections.OrderedDict()

#     def register(self, interface, determinant, field):
#         det = self.interfaces.setdefault(interface, collections.OrderedDict())
#         fields = det.setdefault(determinant, collections.OrderedDict())
#         fields[field] = True


def determinant(field, name=''):
    print(field)
    # registry = getUtility(IDeterminantRegistry)
    field.__determinant__ = name
    return field


class determinants:

    def __init__(self, *args, determinant='primary'):
        self.determinants = args
        self.name = determinant

    def __call__(self, interface):
        attr = "__sql_determinants__"
        if not hasattr(interface, attr):
            interface.__sql_determinants__ = collections.OrderedDict()
        # FIXME: What about determinant definition?
        interface.__sql_determinants__[self.name] = self.determinants
        return(interface)
