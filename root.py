from twisted.web import resource
from schemesettings import schemePresets, schemeDefault
from urllib import quote_plus

class RootResource(resource.Resource):
    def __init__(self, queue):
        self.queue = queue
    def render_GET(self, request):
        out = """

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>LightHandler Web UI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Le styles -->
    <link href="css/bootstrap.css" rel="stylesheet">
    <link href="css/spectrum.css" rel="stylesheet" type="text/css">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    </style>
    <link href="css/bootstrap-responsive.css" rel="stylesheet">

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="js/html5shiv.js"></script>
    <![endif]-->
  </head>

  <body>
    <div class="container-fluid">
      <div class="row-fluid">
        <div class="span12">
          <div class="row-fluid">
            <div class="span4">
              <h2>Set Color</h2>
              <p><input type='text' class="basic" id="pick"/></p>
            </div><!--/span-->
            <div class="span4">
              <h2>Actions</h2>
              <p>
<a href="/flash?r=255&g=0&b=0&times=2&delay=0.25" class="btn">Flash Red</a> 
<a href="/flash?r=0&g=255&b=0&times=2&delay=0.25" class="btn">Flash Green</a> 
<a href="/flash?r=0&g=0&b=255&times=2&delay=0.25" class="btn">Flash Blue</a> 
</p>
            </div><!--/span-->
            <div class="span4">
              <h2>Set Scheme</h2>
              <p>
"""
        for key in schemePresets.keys():
            out += '<a href="/scheme?preset=%s" class="btn">%s</a> ' % (quote_plus(key), key)
        out += """
</p>
            </div><!--/span-->
          </div><!--/row-->
        </div><!--/span-->
      </div><!--/row-->

      <hr>

      <footer>
        <p id="response"></p>
      </footer>

    </div><!--/.fluid-container-->

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
    <script src="js/spectrum.js"></script>
    <script>
        function hexToR(h) {return parseInt((cutHex(h)).substring(0,2),16)}
        function hexToG(h) {return parseInt((cutHex(h)).substring(2,4),16)}
        function hexToB(h) {return parseInt((cutHex(h)).substring(4,6),16)}
        function cutHex(h) {return (h.charAt(0)=="#") ? h.substring(1,7):h}
        $("#pick").spectrum({
            color: "#f00",
            change: function(color) {
                $('#response').load('/color?r='+hexToR(color.toHexString())+'&g='+hexToG(color.toHexString())+'&b='+hexToB(color.toHexString()))
            },
            flat: true
        });
        $('.btn').click(function(e) {
            e.preventDefault();
            $('#response').load($(this).attr('href'));
            return false;
        });
    </script>

  </body>
</html>
"""
        return out