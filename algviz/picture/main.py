from picture import Picture

def make_svg(structure, _, settings):
    pic = Picture.make_picture(structure, **settings)
    pic.draw()
    return pic.getSVG()
