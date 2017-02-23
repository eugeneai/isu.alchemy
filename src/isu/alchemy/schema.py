import collections


class determinants:

    def __init__(self, *args, name='primary'):
        self.determinants = args
        self.name = name

    def __call__(self, interface):
        attr = "__sql_determinants__"
        if not hasattr(interface, attr):
            interface.__sql_determinants__ = collections.OrderedDict()
        # FIXME: What about determinant definition?
        interface.__sql_determinants__[self.name] = self.determinants
        return(interface)
