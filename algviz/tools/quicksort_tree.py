"""
Demonstrates some low-level hacking on our own APIs, by printing a call tree
for a recursive quicksort function.

This whole thing could be done very differently by using our tree-visitor API,
once we have one.  (The two branches of "quicksort" would be performed by the
`get_child()` method of the tree API.)
"""
import random
import sys
import argparse

from algviz.interface import output

def quicksort(items, uid_str, do_a_thing):
    do_a_thing(uid_str, items)
    if len(items) <= 1:
        return items
    pivot = random.choice(items)
    left = quicksort([x for x in items if x < pivot], uid_str + "L", do_a_thing)
    right = quicksort([x for x in items if x > pivot], uid_str + "R", do_a_thing)
    middle = [x for x in items if x == pivot]
    do_a_thing(uid_str + "M", middle)
    return left + middle + right

def mk_qs_node_visitor(output_manager):
    def visit_qs_node(uid_str, items, middle=False):
        nonlocal output_manager
        result = {"uid": uid_str,
                  "type": "treenode",
                  "data": {"type": "array",
                           "data": items}}

        if len(items) > 1 and not middle:
            # This node will have children
            result["children"] = [uid_str + "L", uid_str + "M", uid_str + "R"]
        # `next_val` can print anything that `json.dumps()` accepts:
        output_manager.next_val(result)
    return visit_qs_node

def read_numbers(infile):
    return [float(num) if int(num) != float(num) else int(num) for num in infile.read().split()]

def main():
    parser = argparse.ArgumentParser(
        description="""
        Quick-sort some numbers and print the tree of calls made
        Example usage: `echo 1 8 4 5 6 2 9 | %(prog)s -`
        """)
    parser.add_argument("infile", type=argparse.FileType("r"),
                        help="File with whitespace-separated numbers to sort")
    args = parser.parse_args()
    numbers = read_numbers(args.infile)
    out = output.OutputManager()
    visitor = mk_qs_node_visitor(out)
    with out.start_snapshot():
        quicksort(numbers, "mycalltree", visitor)
    out.end()

if __name__ == "__main__":
    main()
