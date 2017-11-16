Architecture, with some Unix and cayenne pepper for flavor
==========================================================

1. One tool to find code blocks using our extension in markdown files (and feed them to the next tool).

1. One tool (per supported programming language) to process a block of code (maybe multiple blocks of code) and produce descriptions of the data structures.  (This is the part described in introspection_for_visualization.md)

1. One tool to turn descriptions of data structures into beautiful SVGs.

1. One tool to link the SVGs back into the markdown.  (This may or may not be the same as the first tool.  Maybe the first tool also spits out chewed-up markdown for this tool to reinvigorate.)

Reasons for decisions:
======================

1.  Markdown as output:  We hope to add literate programming functionality to markdown without getting in the way of other non-standard markdown extensions.  We'll need to do some research to make sure our syntax doesn't collide with other popular non-standard exensions.

2.  Modularity:

2.1.  The task of turning code (and metadata, i.e. specification of what to visualize) into SGV images has nothing to do with markdown or with our syntax.  Our project is only worthwhile if this component has some merit on its own.  (We hope it can be used to build extensions for LaTeX and other writing tools.)

2.2.  In a similar vein, the actual parsing of the markdown input is almost a triviality and shouldn't be part of the core of the project.  We may even want more than one version of the syntax, especially during development when we don't know how to make it good yet.

2.3.  As discussed in introspection_for_visualization.md, as much work should be done in input-language-independent code as possible.  That's why we want producing a description of the data structure from the code to be cleanly separated from producing an SVG from the description.

2.4.  Linking the SVGs back into the markdown is another part that doesn't belong in the core of the project.  But again, it may be hard to get it right, especially if we want to play nicely with other markdown extensions that handle image-placement more delicately than standard markdown.  (Standard markdown just does ![alt text](/path/to/image.svg), plus a few conveniences like references.  It doesn't do image scaling, for instance.  See https://daringfireball.net/projects/markdown/syntax#img (as of 2017-10-19).)

3.  I don't know where else to say this, but Eyal suggested that the user could specify the image that they want in a special "result block", which would ultimately be replaced by the image in the output markdown file.  That makes a ton of sense.  It's much nicer than the markdown-preview-enhanced syntax where every code block starts with `{run=True, some="parameters", verbosity="extremely verbose considering this is just the start of a code block"}.
