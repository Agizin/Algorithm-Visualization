import svgwrite
size = (500, 500)
doc = svgwrite.Drawing("asdf.svg", size)
doc.add(doc.circle((50, 50), r=25, fill_opacity="0.5"))
doc.add(doc.rect(insert=(40, 50), size=(100, 15), fill_opacity="0.5"))
doc.add(doc.text("Hello, world!", (40, 50), font_size="15px", dy=[1, 2, 3, 4]))
doc.save()
import svgutils.transform as svgutils

old_svg = svgutils.fromfile("asdf.svg")
old_pic = old_svg.getroot()
factor = 0.5

old_pic.scale_xy(x=factor, y=factor)
new_svg = svgutils.SVGFigure(tuple(x * factor for x in size))
new_svg.append([old_pic])
new_svg.save("scaled_asdf.svg")
