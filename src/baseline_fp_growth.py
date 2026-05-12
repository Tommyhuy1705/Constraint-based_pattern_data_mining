from __future__ import annotations

import math
import time
from collections import Counter
from itertools import combinations

from .metrics import average_itemset_price
from .structures import FPTree


def build_fp_tree(weighted_transactions, min_support_count):
    """Build an FP-Tree ordered by descending support."""
    item_counts = Counter()
    for items, weight in weighted_transactions:
        for item in set(items):
            item_counts[item] += weight

    frequent_supports = {
        item: count
        for item, count in item_counts.items()
        if count >= min_support_count
    }
    if not frequent_supports:
        return None

    item_rank = {
        item: rank
        for rank, (item, _) in enumerate(
            sorted(frequent_supports.items(), key=lambda pair: (-pair[1], pair[0]))
        )
    }

    tree = FPTree()
    tree.supports = frequent_supports

    for items, weight in weighted_transactions:
        filtered_items = [item for item in set(items) if item in frequent_supports]
        if filtered_items:
            filtered_items.sort(key=lambda item: item_rank[item])
            tree.add_transaction(filtered_items, count=weight)

    return tree


def conditional_pattern_base(tree, item):
    """Extract the conditional pattern base for an item."""
    base = []
    node = tree.headers.get(item)

    while node is not None:
        path = []
        parent = node.parent
        while parent is not None and parent.item is not None:
            path.append(parent.item)
            parent = parent.parent
        if path:
            path.reverse()
            base.append((path, node.count))
        node = node.link

    return base


def mine_fp_tree(tree, min_support_count, suffix=()):
    """Mine all frequent itemsets from an FP-Tree."""
    patterns = {}
    if tree is None:
        return patterns

    if tree.is_single_path():
        nodes = tree.single_path_nodes()
        path_items = [node.item for node in nodes]
        path_counts = [node.count for node in nodes]

        for size in range(1, len(path_items) + 1):
            for indices in combinations(range(len(path_items)), size):
                itemset = tuple(sorted(tuple(path_items[i] for i in indices) + suffix))
                support_count = min(path_counts[i] for i in indices)
                patterns[itemset] = support_count
        return patterns

    for item, support_count in sorted(tree.supports.items(), key=lambda pair: (pair[1], pair[0])):
        new_suffix = tuple(sorted(suffix + (item,)))
        patterns[new_suffix] = support_count

        conditional_base = conditional_pattern_base(tree, item)
        conditional_tree = build_fp_tree(conditional_base, min_support_count)
        if conditional_tree is not None:
            patterns.update(mine_fp_tree(conditional_tree, min_support_count, new_suffix))

    return patterns


def run_baseline_fp_growth(transactions, item_price, min_support_ratio, price_threshold):
    """Run baseline FP-Growth then filter by avg(price)."""
    min_support_count = math.ceil(min_support_ratio * len(transactions))
    weighted_transactions = [(transaction, 1) for transaction in transactions]

    start_time = time.perf_counter()
    tree = build_fp_tree(weighted_transactions, min_support_count)
    all_patterns = mine_fp_tree(tree, min_support_count)
    final_patterns = {
        itemset: support_count
        for itemset, support_count in all_patterns.items()
        if average_itemset_price(itemset, item_price) <= price_threshold
    }
    runtime_seconds = time.perf_counter() - start_time

    return {
        "min_support_ratio": min_support_ratio,
        "min_support_label": f"{min_support_ratio:.0%}",
        "min_support_count": min_support_count,
        "runtime_seconds": runtime_seconds,
        "all_patterns": all_patterns,
        "final_patterns": final_patterns,
        "num_all_patterns": len(all_patterns),
        "num_final_patterns": len(final_patterns),
        "num_filtered_patterns": len(all_patterns) - len(final_patterns),
    }
