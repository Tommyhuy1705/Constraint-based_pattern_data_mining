from __future__ import annotations


class FPNode:
    """A node in an FP-Tree."""

    __slots__ = ("item", "count", "parent", "children", "link")

    def __init__(self, item, count=0, parent=None):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None


class FPTree:
    """FP-Tree with header table for fast node access."""

    __slots__ = ("root", "headers", "supports")

    def __init__(self):
        self.root = FPNode(item=None, count=0, parent=None)
        self.headers = {}
        self.supports = {}

    def add_transaction(self, ordered_items, count=1):
        current = self.root
        for item in ordered_items:
            child = current.children.get(item)
            if child is None:
                child = FPNode(item=item, count=0, parent=current)
                current.children[item] = child
                child.link = self.headers.get(item)
                self.headers[item] = child
            child.count += count
            current = child

    def is_single_path(self) -> bool:
        current = self.root
        while True:
            if len(current.children) > 1:
                return False
            if not current.children:
                return True
            current = next(iter(current.children.values()))

    def single_path_nodes(self):
        nodes = []
        current = self.root
        while current.children:
            current = next(iter(current.children.values()))
            nodes.append(current)
        return nodes


class PriceFPNode:
    """A node in a price-ordered FP-Tree."""

    __slots__ = ("item", "count", "parent", "children", "link")

    def __init__(self, item=None, count=0, parent=None):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None


class PriceOrderedFPTree:
    """FP-Tree built in ascending price order."""

    __slots__ = ("root", "headers", "supports")

    def __init__(self):
        self.root = PriceFPNode()
        self.headers = {}
        self.supports = {}

    def add_transaction(self, ordered_items):
        current = self.root
        for item in ordered_items:
            child = current.children.get(item)
            if child is None:
                child = PriceFPNode(item=item, count=0, parent=current)
                current.children[item] = child
                child.link = self.headers.get(item)
                self.headers[item] = child
            child.count += 1
            current = child
