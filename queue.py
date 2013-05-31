from twisted.web import resource


class QueueResource(resource.Resource):

    def __init__(self, interface):
        self.interface = interface

    def render_GET(self, request):
        return "%s" % ("ToDo: Fix this")  # ToDo: Fix this
