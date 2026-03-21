"""Chart style defaults for consistent, professional baseball visualizations."""

import matplotlib.pyplot as plt
import matplotlib as mpl

# Your brand font stack (system fonts that look good)
FONT_FAMILY = "Helvetica Neue"
FONT_FALLBACK = "Arial"

# Color palette for non-team charts (light theme)
PALETTE = {
    "dark": "#1a1a2e",
    "medium": "#4a4e69",
    "light": "#9a8c98",
    "accent": "#c9ada7",
    "background": "#ffffff",
    "grid": "#e8e8e8",
    "text": "#2b2d42",
}

# Dark theme palette for @sabrmagician branded visualizations
DARK_THEME = {
    "bg": "#0e1117",
    "card": "#1a1a2e",
    "text": "#e0e0e0",
    "muted": "#8892a0",
    "accent": "#FF6B35",
    "teal": "#4ECDC4",
    "green": "#2ECC71",
    "red": "#E74C3C",
    "gold": "#F1C40F",
    "grid": "#2d2d44",
    "positive": "#4A90D9",  # Colorblind-safe positive (blue)
    "negative": "#E8553D",  # Colorblind-safe negative (red-orange)
}

# Credit line for social media posts
CREDIT = "@sabrmagician"


def apply_style():
    """Apply the project's matplotlib style globally."""
    plt.rcParams.update({
        "figure.facecolor": PALETTE["background"],
        "axes.facecolor": PALETTE["background"],
        "axes.edgecolor": PALETTE["grid"],
        "axes.labelcolor": PALETTE["text"],
        "axes.grid": True,
        "grid.color": PALETTE["grid"],
        "grid.alpha": 0.5,
        "text.color": PALETTE["text"],
        "font.family": "sans-serif",
        "font.sans-serif": [FONT_FAMILY, FONT_FALLBACK],
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "xtick.color": PALETTE["medium"],
        "ytick.color": PALETTE["medium"],
        "legend.framealpha": 0.9,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.3,
    })


def add_credit(fig, text=CREDIT, x=0.99, y=0.01):
    """Add a credit/watermark to the bottom-right of a figure."""
    fig.text(x, y, text, fontsize=8, color=PALETTE["light"],
             ha="right", va="bottom", alpha=0.7)


def plotly_template():
    """Return a Plotly layout template dict matching the matplotlib style."""
    return {
        "paper_bgcolor": PALETTE["background"],
        "plot_bgcolor": PALETTE["background"],
        "font": {"family": f"{FONT_FAMILY}, {FONT_FALLBACK}", "color": PALETTE["text"]},
        "title": {"font": {"size": 16}},
        "xaxis": {"gridcolor": PALETTE["grid"], "linecolor": PALETTE["grid"]},
        "yaxis": {"gridcolor": PALETTE["grid"], "linecolor": PALETTE["grid"]},
    }


def dark_plotly_layout():
    """Return a standard dark theme Plotly layout dict for @sabrmagician charts."""
    return {
        "paper_bgcolor": DARK_THEME["bg"],
        "plot_bgcolor": DARK_THEME["card"],
        "font": {"family": f"{FONT_FAMILY}, {FONT_FALLBACK}", "color": DARK_THEME["text"]},
        "margin": {"t": 80, "b": 60, "l": 60, "r": 40},
    }
