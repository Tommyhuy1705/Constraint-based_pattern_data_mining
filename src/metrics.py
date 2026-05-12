from __future__ import annotations


def average_itemset_price(itemset, price_lookup):
    """Compute average price of an itemset."""
    return sum(float(price_lookup[item]) for item in itemset) / len(itemset)


def patterns_to_dataframe(result, price_lookup, n_transactions):
    """Convert mining results to a DataFrame."""
    import pandas as pd

    rows = []
    for itemset, support_count in result["final_patterns"].items():
        rows.append(
            {
                "Min Support": result["min_support_label"],
                "Itemset": " | ".join(itemset),
                "Kích thước itemset": len(itemset),
                "Support count": support_count,
                "Support": support_count / n_transactions,
                "Avg Price": average_itemset_price(itemset, price_lookup),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    return df.sort_values(
        ["Min Support", "Kích thước itemset", "Support count", "Itemset"],
        ascending=[True, True, False, True],
    ).reset_index(drop=True)


def support_label_to_ratio(label):
    if isinstance(label, str) and label.endswith("%"):
        return float(label[:-1]) / 100
    return float(label)
