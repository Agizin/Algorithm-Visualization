Data structure visualization by introspection
===============================================================================

This is how I would like to do data structure visualization ("the Goal"):

> A language-specific subroutine processes the code and outputs information, in a language-independent format, that can be used to visualize the data structures.

Ways to implement the language-specific subroutines, i.e. "processing the code":

1. Given a piece of code (with some minimal guiding information from the user), modify the code so that it also outputs the desired information as it runs.  Then run the code.

2. Implement our own interpreter / compiler (requires superhuman effort and maintenance)

3. Use a debugger to inspect memory at runtime and extract information about the target data structure (also superhuman effort per language, possibly dependent on compiler)

The first strategy (code modification) should be much easier for most languages, although it's conceivable that we'll find some language where one of the other two ideas works better.

## Comments

This Goal would be achieved if the code always produced the visualization directly, since that could obviously be used to visualize the data structures.

However, if we make the output ("language-independent format") from the code more abstract, we can avoid repeating work.  In particular, it will be much easier to implement visualization for multiple programming languages.  It will also be possible to modify the representation of the same abstract data structure independently of the language.  (The task outlined in the Goal above may be the most difficult part of the project.  The more elegant our solution to this problem, the better.)

For exaple, say that to visualize a tree used in some piece of code, you cause the code to print descriptions of the nodes of the tree.  Then in the main (language-independent) code, there can be multiple routines available to process the description and produce a visualization.  These routines can draw the tree with different layouts, different representations of the nodes, different colors and styles, etc.


Case for using a visitor pattern in most cases (for the language specific code)
===============================================================================

We get enough information from the user that we can automatically implement a visitor for the data structure.  This has the advantage of leaving the data structure completely untouched, in the best case.

### comments on Visitor idea:

Good languages for visitor:  Python, Lisp, C, anything functional.

Good structures for visitor:  any structure that can be examined non-destructively, e.g. a linked list.

Bad example for visitor:  A cache implemented in Java, where the only exposed methods are mutative.  E.g. Cache.lookup($key$), which returns the value corresponding to $key$ and mutates the cache so that $key$ can be found more easily.

Workaround for Java (step by step):

1.  In class to be visualized (the "Target"), the properties necessary for visualization must be made protected or public, not private.  (This is a limitation.)

2.  Make a subclass `S` of the Target.  `S` accesses protected properties of Target and exposes an interface to the standard Visitor for Target.  (This part will be hard, but if Java has any merit at all, something along these lines will be possible.)

Good example for visitor:  Binary search tree.  See tree_visitor_example.py

