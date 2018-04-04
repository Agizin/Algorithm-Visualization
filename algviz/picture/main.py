from . import layout_dispatch, svg, rec_layout


def layout_and_draw(obj):
    choose_layout = layout_dispatch.make_layout_chooser({})
    drawer = svg.default_full_drawer()
    layout = rec_layout.create_layout(obj, svg_hint=drawer.hint,
                                      choose_layout=choose_layout)
    return drawer.layout_to_svg(layout)
