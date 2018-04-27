from setuptools import setup, find_packages

version = '0.0.1'

setup(name='algviz',
      version=version,
      author=['Anna Gorbenko', 'Jonathan Homburg', 'John McGowan', 'Doni Ivanov', 'Eyal Minsky-Fenick', 'Oliver Kisielius'],  # feel free to change this, too
      url=r'https://github.com/Agizin/Algorithm-Visualization',
      packages=find_packages(exclude=['ez_setup',]),
      entry_points={
          "console_scripts": [
              "algviz_graph_mockup=algviz.tools.graph_drawing_mockup:main",
              "algviz_quicksort_example=algviz.tools.quicksort_tree:main",
              "algviz_rec_draw=algviz.tools.draw_recursive_pic:main",
              "algviz_random_tree=algviz.tools.bin_tree_maker:main",
          ]},
      install_requires=[
          'pygraphviz',
          'svgutils'
      ],
)
