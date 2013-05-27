from twisted.web import resource

class FadetimeResource(resource.Resource):
    def __init__(self, queue):
        self.queue = queue
    def render_GET(self, request):
        fadetime = int(request.args["fadetime"][0])
        self.queue.append(["fadetime", fadetime])
        return "Appended fadetime update"