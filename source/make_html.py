import os
here = os.path.dirname(os.path.abspath(__file__))
three = open(os.environ.get("THREE_JS", os.path.join(here, "three.min.js")), encoding="utf8").read()   # three.js r147 (three.min.js)
data = open(os.path.join(here, "meshes.json"), encoding="utf8").read()
html = open(os.path.join(here, "page_template.tpl"), encoding="utf8").read()
html = html.replace("__THREE__", three.replace("</script", "<\\/script")).replace("__DATA__", data)
out = os.path.join(here, "reducteur_125_3D.html")
open(out, "w", encoding="utf8").write(html)
print("ecrit reducteur_125_3D.html : %.1f Mo" % (os.path.getsize(out) / 1e6))
