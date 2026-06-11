#!/usr/bin/env python3
"""
visualization/plot_results.py

Visualization Engine Version 1 for the TruthRetainBench benchmark.
Generates publication-quality charts from computed session metrics
and saves them as PNG files in results/figures/.
"""

import os
import sys
import matplotlib.pyplot as plt

# Ensure parent directory is in sys.path to resolve metrics imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from metrics.metrics_engine import load_dataset_csv, analyze_sessions
except ImportError as e:
    # Fallback to local import if run differently
    print(f"Warning: Absolute imports failed, attempting local imports. Details: {e}", file=sys.stderr)
    from metrics_engine import load_dataset_csv, analyze_sessions


def setup_plot_style() -> None:
    """
    Sets up a clean, modern, publication-quality style for matplotlib plots.
    """
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
    plt.rcParams['axes.edgecolor'] = '#cccccc'
    plt.rcParams['axes.linewidth'] = 0.8
    plt.rcParams['xtick.color'] = '#555555'
    plt.rcParams['ytick.color'] = '#555555'
    plt.rcParams['grid.color'] = '#e2e8f0'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.5


def plot_domain_pass_rates(metrics: dict, save_path: str) -> None:
    """
    Generates a bar chart for Pass Rate by Domain.
    """
    domains = list(metrics["domain_metrics"].keys())
    pass_rates = []
    for d in domains:
        data = metrics["domain_metrics"][d]
        eval_count = data["evaluated"]
        rate = (data["pass"] / eval_count * 100) if eval_count > 0 else 0.0
        pass_rates.append(rate)

    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Visual elements: clean blue color and elegant borders
    bars = ax.bar(domains, pass_rates, color='#3b82f6', width=0.55, edgecolor='#1d4ed8', linewidth=0.8, zorder=3)
    
    ax.set_ylabel("Pass Rate (%)", fontsize=11, fontweight='semibold', color='#333333', labelpad=10)
    ax.set_xlabel("Domain", fontsize=11, fontweight='semibold', color='#333333', labelpad=10)
    ax.set_title("Pass Rate by Domain", fontsize=14, fontweight='bold', color='#1e293b', pad=20)
    ax.set_ylim(0, 105)
    ax.grid(axis='y', zorder=0)
    ax.set_axisbelow(True)

    # Clean styling: hide top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')

    # Add numeric labels on top of the bars
    ax.bar_label(bars, fmt='%.1f%%', padding=5, fontsize=10, fontweight='semibold', color='#1e293b')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_qtype_pass_rates(metrics: dict, save_path: str) -> None:
    """
    Generates a bar chart for Pass Rate by Question Type (T1 to T5).
    """
    qtypes = list(metrics["qtype_metrics"].keys())
    pass_rates = []
    for qt in qtypes:
        data = metrics["qtype_metrics"][qt]
        eval_count = data["evaluated"]
        rate = (data["pass"] / eval_count * 100) if eval_count > 0 else 0.0
        pass_rates.append(rate)

    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Visual elements: clean emerald/green color and elegant borders
    bars = ax.bar(qtypes, pass_rates, color='#10b981', width=0.55, edgecolor='#047857', linewidth=0.8, zorder=3)
    
    ax.set_ylabel("Pass Rate (%)", fontsize=11, fontweight='semibold', color='#333333', labelpad=10)
    ax.set_xlabel("Question Type", fontsize=11, fontweight='semibold', color='#333333', labelpad=10)
    ax.set_title("Pass Rate by Question Type", fontsize=14, fontweight='bold', color='#1e293b', pad=20)
    ax.set_ylim(0, 105)
    ax.grid(axis='y', zorder=0)
    ax.set_axisbelow(True)

    # Clean styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')

    # Add labels on top of the bars
    ax.bar_label(bars, fmt='%.1f%%', padding=5, fontsize=10, fontweight='semibold', color='#1e293b')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_failure_distribution(metrics: dict, save_path: str) -> None:
    """
    Generates a bar chart for Failure Distribution (FL1 to FL6).
    """
    codes = list(metrics["failure_distribution"].keys())
    counts = list(metrics["failure_distribution"].values())

    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Visual elements: clean red/coral color and elegant borders
    bars = ax.bar(codes, counts, color='#f43f5e', width=0.55, edgecolor='#be123c', linewidth=0.8, zorder=3)
    
    ax.set_ylabel("Failure Count", fontsize=11, fontweight='semibold', color='#333333', labelpad=10)
    ax.set_xlabel("Failure Code", fontsize=11, fontweight='semibold', color='#333333', labelpad=10)
    ax.set_title("Failure Mode Distribution", fontsize=14, fontweight='bold', color='#1e293b', pad=20)
    
    max_count = max(counts) if counts else 0
    ax.set_ylim(0, max(max_count + 2, 5))
    ax.grid(axis='y', zorder=0)
    ax.set_axisbelow(True)

    # Clean styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')

    # Add integer count labels on top of bars
    ax.bar_label(bars, fmt='%d', padding=5, fontsize=10, fontweight='semibold', color='#1e293b')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_tpi_card(metrics: dict, save_path: str) -> None:
    """
    Generates a stylized metric card for Truth Pressure Index (TPI).
    """
    tpi = metrics["tpi"]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#f8fafc')  # Soft slate background
    ax.set_facecolor('#ffffff')        # Clean white card surface
    
    # Card borders
    ax.spines['top'].set_color('#e2e8f0')
    ax.spines['bottom'].set_color('#e2e8f0')
    ax.spines['left'].set_color('#e2e8f0')
    ax.spines['right'].set_color('#e2e8f0')
    ax.spines['top'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['right'].set_linewidth(1.5)
    
    # Remove tick marks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Draw central metric visual text
    ax.text(0.5, 0.65, f"{tpi:.2f}%", fontsize=52, fontweight='bold', ha='center', va='center', color='#2563eb')
    ax.text(0.5, 0.38, "Truth Pressure Index (TPI)", fontsize=16, fontweight='bold', ha='center', va='center', color='#1e293b')
    ax.text(0.5, 0.22, "Model resistance to external misinformation pressure", fontsize=10, style='italic', ha='center', va='center', color='#64748b')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()


def main() -> None:
    # Set paths relative to project root
    csv_path = os.path.join(parent_dir, "dataset", "TruthRetainBench_v2.csv")
    raw_dir = os.path.join(parent_dir, "results", "raw")
    figures_dir = os.path.join(parent_dir, "results", "figures")
    
    # Ensure figures output directory exists
    os.makedirs(figures_dir, exist_ok=True)
    
    print("Loading dataset and analyzing session logs...")
    dataset_map = load_dataset_csv(csv_path)
    metrics = analyze_sessions(raw_dir, dataset_map)
    
    # Configure Matplotlib theme style
    setup_plot_style()
    
    # Define save paths
    domain_path = os.path.join(figures_dir, "pass_rate_by_domain.png")
    qtype_path = os.path.join(figures_dir, "pass_rate_by_qtype.png")
    failure_path = os.path.join(figures_dir, "failure_distribution.png")
    tpi_path = os.path.join(figures_dir, "truth_pressure_index.png")
    
    # Generate and save figures
    print("\nGenerating charts...")
    
    plot_domain_pass_rates(metrics, domain_path)
    print(f"Saved Pass Rate by Domain chart to: {domain_path}")
    
    plot_qtype_pass_rates(metrics, qtype_path)
    print(f"Saved Pass Rate by Question Type chart to: {qtype_path}")
    
    plot_failure_distribution(metrics, failure_path)
    print(f"Saved Failure Distribution chart to: {failure_path}")
    
    plot_tpi_card(metrics, tpi_path)
    print(f"Saved Truth Pressure Index (TPI) card to: {tpi_path}")
    
    print("\nVisualization generation complete!")


if __name__ == "__main__":
    main()
