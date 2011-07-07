from django_xmlrpc.views import xmlrpcdispatcher

def xmlrpc(uri):
    """A decorator for XML-RPC functions."""
    def register_xmlrpc(fn, *args, **kw):
        xmlrpcdispatcher.register_function(fn, uri)
        return fn
    return register_xmlrpc