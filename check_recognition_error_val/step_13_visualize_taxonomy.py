# category_distribution.py
import argparse
import ast
import math
import os
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv
load_dotenv()
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import matplotlib.pyplot as plt


CATEGORY_COLS = ["Category 1", "Category 2", "Category 3", "Category 4"]


def is_nan(x: Any) -> bool:
    try:
        return x is None or (isinstance(x, float) and math.isnan(x))
    except Exception:
        return False


def parse_as_list(value: Any) -> List[Any]:
    """
    Try to interpret a CSV cell as a list.

    Supported examples:
      - "['a','b']" / "[1, 2]" / "('a','b')" / "{'a','b'}"  -> parsed by literal_eval
      - "a, b, c" or "a;b;c"                               -> split into list (fallback)
      - "" / NaN / None / "0" / "None" / "nan"             -> []
      - a single scalar (e.g., "abc")                       -> []  (treat as not-a-list by default)

    If you DO want "abc" to count as 1, change the final return to [value].
    """
    if is_nan(value):
        return []

    s = str(value).strip()
    if s == "" or s.lower() in {"none", "null", "nan"}:
        return []

    # First try python-literal formats: [], (), {}, set(...)
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, tuple):
            return list(parsed)
        if isinstance(parsed, set):
            return list(parsed)
        # If it's something else (dict/number/string), treat as not-a-list
        return []
    except Exception:
        pass

    # Fallback: comma/semicolon separated tokens -> treat as list
    # Only if it "looks like" a multi-item list.
    if ("," in s) or (";" in s) or ("|" in s):
        sep = "," if "," in s else (";" if ";" in s else "|")
        items = [t.strip() for t in s.split(sep)]
        items = [t for t in items if t != ""]
        return items

    # Otherwise treat as not-a-list
    return []


def cell_list_len(value: Any) -> int:
    return len(parse_as_list(value))


def compute_category_counts_and_ratios(df: pd.DataFrame, category_cols: List[str]) -> Tuple[Dict[str, int], Dict[str, float]]:
    counts: Dict[str, int] = {}
    for col in category_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'. Found columns: {list(df.columns)}")
        counts[col] = int(df[col].apply(cell_list_len).sum())

    total = sum(counts.values())
    if total == 0:
        ratios = {k: 0.0 for k in counts}
    else:
        ratios = {k: counts[k] / total for k in counts}

    return counts, ratios


def plot_category_distribution(
    counts: Dict[str, int],
    ratios: Dict[str, float],
    title: str = "Category Distribution",
    save_path: str = "",
):
    labels = list(counts.keys())
    y = [ratios[k] for k in labels]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, y)

    ax.set_title(title)
    ax.set_ylabel("Ratio")
    ax.set_ylim(0, max(0.05, max(y) * 1.25 if len(y) > 0 else 1.0))
    ax.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.6)

    # annotate: "12.3% (45)"
    for rect, k in zip(bars, labels):
        height = rect.get_height()
        c = counts[k]
        txt = f"{height*100:.1f}% ({c})"
        ax.text(
            rect.get_x() + rect.get_width() / 2,
            height,
            txt,
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200)
        print(f"[OK] Saved plot to: {save_path}")
    else:
        plt.show()


def main(csv_name: str, save_path: str | None = r""):
    # parser = argparse.ArgumentParser(description="Compute category ratios from CSV and plot a bar chart.")
    # parser.add_argument("--csv", default=csv_name, help="Path to input CSV")
    # parser.add_argument("--save", default=save_path, help="Optional path to save the plot (e.g., out.png). If empty -> show window.")
    # parser.add_argument("--title", default="", help="Plot title")
    # args = parser.parse_args()

    if not os.path.exists(csv_name):
        raise FileNotFoundError(f"CSV not found: {csv_name}")

    df = pd.read_csv(csv_name)

    counts, ratios = compute_category_counts_and_ratios(df, CATEGORY_COLS)

    print("=== Counts ===")
    for k in CATEGORY_COLS:
        print(f"{k}: {counts[k]}")

    total = sum(counts.values())
    print(f"Total (all categories): {total}")

    print("\n=== Ratios ===")
    for k in CATEGORY_COLS:
        print(f"{k}: {ratios[k]*100:.2f}%")

    if save_path:
        plot_category_distribution(counts, ratios, title="", save_path=save_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task_name", type=str, default="v6_Gemini_3")
    parser.add_argument("--model_name", type=str, default="gemini-3-pro-preview")
    parser.add_argument("--split_name", type=str, default="observation")
    args = parser.parse_args()
    
    set_type_map = {"observation": "obsetf"}
    if args.split_name not in set_type_map:
        raise ValueError(f"Unsupported split name: {args.split_name}. Valid options are: {list(set_type_map.keys())}")
    SET_TYPE = set_type_map[args.split_name]
    model_name = args.model_name.split("/")[-1]
    JUDGE_MODEL_NAME = "models/gemini-2.5-pro"
    safe_judge_name = JUDGE_MODEL_NAME.split('/')[-1]
    
    input_path = os.path.join("Recognition_Detection_outputs", "rechecked", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
    output_path = os.path.join("Recognition_Detection_outputs", "rechecked_taxonomy", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
    save_path = rf""
    main(output_path, save_path)
