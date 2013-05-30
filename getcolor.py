from twisted.web import resource

class GetColorResource(resource.Resource):
    def __init__(self, interface):
        self.interface = interface
    def render_GET(self, request):
        return "%s" % self.interface.current
