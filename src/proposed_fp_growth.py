from __future__ import annotations

import math
import time

from .structures import PriceOrderedFPTree


def count_tree_nodes(tree) -> int:
    """Count the number of non-root nodes in an FP-Tree."""
    node_count = 0
    stack = list(tree.root.children.values())
    while stack:
        node = stack.pop()
        node_count += 1
        stack.extend(node.children.values())
    return node_count


def max_tree_depth(tree) -> int:
    """Compute the maximum depth of an FP-Tree."""
    max_depth = 0
    stack = [(child, 1) for child in tree.root.children.values()]
    while stack:
        node, depth = stack.pop()
        max_depth = max(max_depth, depth)
        stack.extend((child, depth + 1) for child in node.children.values())
    return max_depth


def build_item_tid_bitsets(transactions, price_lookup):
    """Build a bitset index of transactions containing each item."""
    item_bitsets = {}
    for tid, transaction in enumerate(transactions):
        transaction_bit = 1 << tid
        for item in set(transaction):
            if item in price_lookup:
                item_bitsets[item] = item_bitsets.get(item, 0) | transaction_bit
    return item_bitsets


def build_price_ordered_fp_tree(transactions, frequent_items, price_rank):
    """Build an FP-Tree ordered by ascending price."""
    frequent_item_set = set(frequent_items)
    tree = PriceOrderedFPTree()
    tree.supports = {}

    for transaction in transactions:
        ordered_items = sorted(
            set(item for item in transaction if item in frequent_item_set),
            key=lambda item: price_rank[item],
        )
        if ordered_items:
            tree.add_transaction(ordered_items)

    return tree


def run_proposed_in_mining_pruning(
    transactions,
    item_price,
    item_bitsets,
    min_support_ratio,
    price_threshold,
):
    """Run the proposed price-ordered FP-Growth with in-mining pruning."""
    min_support_count = math.ceil(min_support_ratio * len(transactions))
    price_ordered_items = sorted(item_price, key=lambda item: (item_price[item], item))
    price_rank = {item: rank for rank, item in enumerate(price_ordered_items)}

    start_time = time.perf_counter()

    frequent_items = [
        item
        for item in price_ordered_items
        if item_bitsets.get(item, 0).bit_count() >= min_support_count
    ]

    fp_tree = build_price_ordered_fp_tree(transactions, frequent_items, price_rank)
    all_transaction_bits = (1 << len(transactions)) - 1

    final_patterns = {}
    stats = {
        "root_frequent_items": len(frequent_items),
        "fp_tree_nodes": count_tree_nodes(fp_tree),
        "fp_tree_max_depth": max_tree_depth(fp_tree),
        "recursive_calls": 0,
        "candidate_evaluations": 0,
        "support_evaluations": 0,
        "infrequent_candidates": 0,
        "price_pruned_candidates": 0,
        "max_pattern_length": 0,
    }

    def dfs(start_index, prefix, prefix_price_sum, prefix_tid_bits):
        stats["recursive_calls"] += 1
        stats["max_pattern_length"] = max(stats["max_pattern_length"], len(prefix))

        for item_index in range(start_index, len(frequent_items)):
            item = frequent_items[item_index]
            stats["candidate_evaluations"] += 1

            candidate_price_sum = prefix_price_sum + item_price[item]
            candidate_length = len(prefix) + 1
            candidate_avg_price = candidate_price_sum / candidate_length

            if candidate_avg_price > price_threshold:
                stats["price_pruned_candidates"] += len(frequent_items) - item_index
                break

            stats["support_evaluations"] += 1
            candidate_tid_bits = prefix_tid_bits & item_bitsets[item]
            support_count = candidate_tid_bits.bit_count()

            if support_count >= min_support_count:
                candidate = prefix + (item,)
                canonical_candidate = tuple(sorted(candidate))
                final_patterns[canonical_candidate] = support_count
                dfs(item_index + 1, candidate, candidate_price_sum, candidate_tid_bits)
            else:
                stats["infrequent_candidates"] += 1

    dfs(0, tuple(), 0.0, all_transaction_bits)
    runtime_seconds = time.perf_counter() - start_time

    return {
        "min_support_ratio": min_support_ratio,
        "min_support_label": f"{min_support_ratio:.0%}",
        "min_support_count": min_support_count,
        "runtime_seconds": runtime_seconds,
        "final_patterns": final_patterns,
        "num_final_patterns": len(final_patterns),
        "stats": stats,
    }
