from twisted.web import resource
from schemesettings import schemePresets, schemeDefault

class SchemeResource(resource.Resource):
    def __init__(self, queue):
        self.queue = queue
    def render_GET(self, request):
        preset = request.args["preset"][0]
        if not preset in schemePresets:
            request.setResponseCode(500)
            return "Unknown preset"
        self.queue.append(["scheme", preset])
        return "Appended scheme update event to %s" % preset