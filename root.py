from twisted.web import resource
from schemesettings import schemePresets, schemeDefault
from urllib import quote_plus

class RootResource(resource.Resource):
    def __init__(self, queue):
        self.queue = queue
    def render_GET(self, request):
        out = """
<LINK href="http://bgrins.github.com/spectrum/spectrum.css" rel="stylesheet" type="text/css">
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
<script src="http://bgrins.github.com/spectrum/spectrum.js"></script>
<style>
body{background-color:black;}
</style>
<input type='text' class="basic" id="pick"/>
<br />
<div style="background-color:white">
"""
        for key in schemePresets.keys():
            out += '<input type="button" url="/scheme?preset=%s" class="ajaxify" value="%s" /> ' % (quote_plus(key), key)
        out += """
<br />
<input type="button" url="/flash?r=255&g=0&b=0&times=2&delay=0.25" class="ajaxify" value="Flash Red" /> 
<input type="button" url="/flash?r=0&g=255&b=0&times=2&delay=0.25" class="ajaxify" value="Flash Green" /> 
<input type="button" url="/flash?r=0&g=0&b=255&times=2&delay=0.25" class="ajaxify" value="Flash Blue" /> 
</div>
<div id="response" style="background-color:white">test</div>
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
$('.ajaxify').click(function(e) {
e.preventDefault();
$('#response').load($(this).attr('url'));
});
</script>"""
        return out