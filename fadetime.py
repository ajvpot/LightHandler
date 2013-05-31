from twisted.web import resource


class FadetimeResource(resource.Resource):

    def __init__(self, interface):
        self.interface = interface

    def render_GET(self, request):
        fadetime = int(request.args["fadetime"][0])
        self.interface.queueEvent(["fadetime", fadetime])
        return "Appended fadetime update"
