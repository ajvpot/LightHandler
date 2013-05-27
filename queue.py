from twisted.web import resource

class QueueResource(resource.Resource):
    def __init__(self, queue):
        self.queue = queue
    def render_GET(self, request):
        return "%s" % (self.queue)