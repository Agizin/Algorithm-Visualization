# UConn Language Independent Descriptions of Structures

Or just Lazy Indifferent Data Structures, or Design by Seniors.  The UCLIDS thing happened by accident, but now I don't want to give it up.

# This is a draft

Some stuff is still wrong:

1.  Literals probably need cleaning up

2.  Feedback is welcome in general

2.  Syntax in example blocks is inconsistent because I was experimenting while writing the documentation.  I know it's atrocious.

# Syntax

## Comments

End-of-line comments will begin with `#`, the Comment Marker.

Probably `#` is as good a choice as any, but this choice was arbitrary.

## Labels

A Label is a string matching this quoted regex: "[a-zA-Z_][a-zA-Z0-9_]*".  A Label is used as a name for a thing.

In the future, the regex for Labels could be relaxed if cases arrise where the most natural identifier for an object contains punctuation.  However, whitespace, parentheses and curly braces, and Comment Markers will never be allowed in Labels.  (I.e. 0x9, 0xa, 0x20, 0x23, 0x28, 0x29, 0x7b, and 0x7d.)

## Blocks

A specification of a single instance of a data structure happens in a Block.  A Block looks like this:

```
{block_type_name|content of the Block}
```

%% no, not like this.  commented out.  Ignore this.
%% ```
%% block_type_name ( unique_id_of_data_structure ) { content of the Block }
%% ```

where:

+   `block_type_name` is a Label specifying what the format (and meaning) of the Block content will be.

%% Not this.. Ignore this, unless I decide it's a good idea tomorrow
%% +   `unique_id_of_data_structure` is a Label that can be used, among other things, by an end user who wants to specify how to display the data structure.  It might not need to be unique.

+   The content of the block should be recognized by the specific parser for Blocks of type `block_type_name`.

+   Every Block should define a primary Label that can be used to refer to the data structure created in the block.  For example, for a `binary_tree_block`, this could be a Label of the root node.

+   Whitespace is not important, except possibly inside the curly braces.

### Block example

```
binary_tree_block (my_example_tree) {
my_example_tree --root--> ArrayTree139802429787208at0 --with-data-- 1
ArrayTree139802429787208at0 --left--> ArrayTree139802429787208at1 --with-data-- 2
ArrayTree139802429787208at1 --left--> ArrayTree139802429787208at3 --with-data-- 4
ArrayTree139802429787208at1 --right--> ArrayTree139802429787208at4 --with-data-- 5
ArrayTree139802429787208at0 --right--> ArrayTree139802429787208at2 --with-data-- 3
ArrayTree139802429787208at2 --left--> ArrayTree139802429787208at5 --with-data-- 6
} # end of binary_tree_block
```

Here we define `my_example_tree`, which is an instance of a data structure of type binary_tree_block.  `my_example_tree` has 6 nodes, each of which stores a single integer as data.  Here, the Labels identifying the nodes were obviously generated programatically, because they are hideous.  However, one could write the same tree by hand like so:

```
binary_tree_block (my_prettier_tree) {
--root--> node0
  node0 --left--> node1 --with-data-- 2
    node1 --left--> node3 --with-data-- 4
    node1 --right--> node4 --with-data-- 5
  node0 --right--> node2 --with-data-- 3
    node2 --left--> node5 --with-data-- 6
}

## Primitive data types and nested Blocks

Data structures should be able to store data.  (At least out in the Industry.)  But that data could be made of yet more data structures.  So, blocks may need to be nested.

Problem:  You should be able to have a nested block, but you should also be able to refer to a structure already defined.  But, how do you know the data structure to which you refer has not been modified since it was put into code?

Solution:  Top-level blocks cannot refer to each other at all.  This is useful because each top-level block describes the state of a structure _at a particular time_.  (If we're generating the UCLIDS at runtime, then this statement holds as long as the data structure isn't modified while its UCLIDS Block is generated.)

Anyway, here's how it goes.  You can inline a block, as in

```
binary_tree_block (my_tree_of_trees) {
my_example_tree --root--> ArrayTree139802429787208at0 --with-data-- 1
--root--> node0
node0 --left--> node1 --with-data-- {binary_tree_block|my_tree1 ; --root--> node0 --data-- "hello"; etc}
node1 --left--> node3 --with-data-- 4
}
```

### Primitive types

A plain integer `35` is syntactic sugar for `{primitive_int|35}`

A double-quoted string "asdf" is syntactic sugar for `{primitive_str|35}`

A value with C-style dereferencing, like `&VAL`, is syntactic sugar for `{ptr|VAL}`, e.g. `&5` means `{ptr|5}`, which means `{ptr|{primitive_int|5}}`.

TODO:  I can't remember other primitive data types right now because it's 1:05 AM.  So I'll work on this later.