from twisted.web import resource

class SetIntensityResource(resource.Resource):
    def __init__(self, queue):
        self.queue = queue
    def render_GET(self, request):
        self.queue.max = int(request.args["intensity"][0])/float(100)
        return "Set intensity to %s" % self.queue.max