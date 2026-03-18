"""Hitter vs Pitcher Matchup Explorer

A Streamlit app to analyze individual matchups using Statcast data.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Required for Streamlit
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from src.utils.db import query

# Dark theme colors
DARK_BG = "#1C2331"
CARD_BG = "#232D3F"
ACCENT = "#22D1EE"
TEXT_WHITE = "#E8E8E8"
TEXT_DIM = "#7A8BA0"

st.set_page_config(layout="wide", page_title="Matchup Explorer")

# Apply dark theme styling
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {DARK_BG};
    }}
    .stSelectbox label, .stMetric label {{
        color: {TEXT_DIM} !important;
    }}
    .stMetric {{
        background-color: {CARD_BG};
        padding: 1rem;
        border-radius: 0.5rem;
    }}
    h1, h2, h3 {{
        color: {TEXT_WHITE} !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("Hitter vs Pitcher Matchup Explorer")

# Cache data queries
@st.cache_data
def get_batters():
    """Get all unique batters from statcast data."""
    df = query("""
        SELECT DISTINCT
            sp.batter,
            p.name_first || ' ' || p.name_last as batter_name
        FROM statcast_pitches sp
        JOIN player_ids p ON sp.batter = p.key_mlbam
        WHERE p.name_first IS NOT NULL
        ORDER BY batter_name
    """)
    return df

@st.cache_data
def get_pitchers():
    """Get all unique pitchers from statcast data."""
    df = query("""
        SELECT DISTINCT player_name as pitcher_name
        FROM statcast_pitches
        WHERE player_name IS NOT NULL
        ORDER BY player_name
    """)
    return df

@st.cache_data
def get_matchup_data(batter_id, pitcher_name):
    """Get head-to-head matchup data if it exists."""
    # Escape single quotes in pitcher name to prevent SQL injection
    safe_pitcher_name = pitcher_name.replace("'", "''")
    df = query(f"""
        SELECT *
        FROM statcast_pitches
        WHERE batter = {batter_id}
        AND player_name = '{safe_pitcher_name}'
        ORDER BY game_date, at_bat_number, pitch_number
    """)
    return df

@st.cache_data
def get_pitcher_data(pitcher_name):
    """Get all pitches thrown by a pitcher."""
    # Escape single quotes in pitcher name to prevent SQL injection
    safe_pitcher_name = pitcher_name.replace("'", "''")
    df = query(f"""
        SELECT *
        FROM statcast_pitches
        WHERE player_name = '{safe_pitcher_name}'
    """)
    return df

@st.cache_data
def get_batter_data(batter_id):
    """Get all pitches faced by a batter."""
    df = query(f"""
        SELECT *
        FROM statcast_pitches
        WHERE batter = {batter_id}
    """)
    return df

# Load player lists
batters_df = get_batters()
pitchers_df = get_pitchers()

# Selection UI
col1, col2 = st.columns(2)

with col1:
    selected_batter = st.selectbox(
        "Select Batter",
        options=batters_df['batter_name'].tolist(),
        index=None,
        placeholder="Choose a batter..."
    )

with col2:
    selected_pitcher = st.selectbox(
        "Select Pitcher",
        options=pitchers_df['pitcher_name'].tolist(),
        index=None,
        placeholder="Choose a pitcher..."
    )

# Only show analysis if both players are selected
if selected_batter and selected_pitcher:
    # Get batter ID
    batter_id = batters_df[batters_df['batter_name'] == selected_batter]['batter'].iloc[0]

    # Get data
    matchup_df = get_matchup_data(batter_id, selected_pitcher)
    pitcher_df = get_pitcher_data(selected_pitcher)
    batter_df = get_batter_data(batter_id)

    # Get batter handedness (most common stand)
    batter_hand = batter_df['stand'].mode()[0] if len(batter_df) > 0 else 'R'
    pitcher_hand = pitcher_df['p_throws'].mode()[0] if len(pitcher_df) > 0 else 'R'

    st.markdown("---")

    # Head-to-head section
    st.header(f"{selected_batter} ({batter_hand}) vs {selected_pitcher} ({pitcher_hand})")

    if len(matchup_df) > 0:
        # Filter to balls in play
        bip = matchup_df[matchup_df['launch_speed'].notna()]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Pitches", len(matchup_df))
        with col2:
            st.metric("At Bats", matchup_df['at_bat_number'].nunique())
        with col3:
            avg_ev = bip['launch_speed'].mean() if len(bip) > 0 else 0
            st.metric("Avg Exit Velo", f"{avg_ev:.1f} mph")
        with col4:
            avg_xwoba = bip['estimated_woba_using_speedangle'].mean() if len(bip) > 0 else 0
            st.metric("Avg xwOBA", f"{avg_xwoba:.3f}")
    else:
        st.info("No head-to-head matchup data found between these players.")

    st.markdown("---")

    # Pitcher analysis
    st.header("Pitcher Analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Pitch Mix")

        # Calculate pitch mix
        pitch_mix = pitcher_df.groupby('pitch_name').size().reset_index(name='count')
        pitch_mix['pct'] = 100 * pitch_mix['count'] / pitch_mix['count'].sum()
        pitch_mix = pitch_mix.sort_values('pct', ascending=True)

        # Create pitch mix bar chart
        fig, ax = plt.subplots(figsize=(8, 6), facecolor=DARK_BG)
        ax.set_facecolor(CARD_BG)

        bars = ax.barh(pitch_mix['pitch_name'], pitch_mix['pct'], color=ACCENT)
        ax.set_xlabel('Usage %', color=TEXT_WHITE)
        ax.set_ylabel('Pitch Type', color=TEXT_WHITE)
        ax.tick_params(colors=TEXT_WHITE)
        ax.spines['bottom'].set_color(TEXT_DIM)
        ax.spines['left'].set_color(TEXT_DIM)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Add percentage labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{width:.1f}%', ha='left', va='center', color=TEXT_WHITE, fontsize=9)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader(f"Pitch Locations vs {batter_hand}HH")

        # Filter pitcher data to same handedness as batter
        pitcher_vs_hand = pitcher_df[pitcher_df['stand'] == batter_hand]

        if len(pitcher_vs_hand) > 0:
            # Filter to pitches with location data
            loc_data = pitcher_vs_hand[
                pitcher_vs_hand['plate_x'].notna() &
                pitcher_vs_hand['plate_z'].notna()
            ]

            if len(loc_data) > 0:
                # Create strike zone heatmap
                fig, ax = plt.subplots(figsize=(8, 8), facecolor=DARK_BG)
                ax.set_facecolor(CARD_BG)

                # Strike zone boundaries (approximate)
                zone_width = 17/12  # 17 inches in feet
                zone_top = 3.5
                zone_bottom = 1.5

                # Draw strike zone
                zone = patches.Rectangle(
                    (-zone_width/2, zone_bottom),
                    zone_width,
                    zone_top - zone_bottom,
                    linewidth=2,
                    edgecolor=TEXT_DIM,
                    facecolor='none'
                )
                ax.add_patch(zone)

                # Create 2D histogram (heatmap)
                h = ax.hexbin(
                    loc_data['plate_x'],
                    loc_data['plate_z'],
                    gridsize=20,
                    cmap='YlOrRd',
                    alpha=0.8,
                    mincnt=1
                )

                ax.set_xlim(-2, 2)
                ax.set_ylim(0, 5)
                ax.set_xlabel('Horizontal Location (ft)', color=TEXT_WHITE)
                ax.set_ylabel('Vertical Location (ft)', color=TEXT_WHITE)
                ax.tick_params(colors=TEXT_WHITE)
                ax.spines['bottom'].set_color(TEXT_DIM)
                ax.spines['left'].set_color(TEXT_DIM)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

                # Add colorbar
                cbar = plt.colorbar(h, ax=ax)
                cbar.ax.yaxis.set_tick_params(color=TEXT_WHITE)
                plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=TEXT_WHITE)
                cbar.set_label('Pitch Count', color=TEXT_WHITE)

                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            else:
                st.warning("No pitch location data available.")
        else:
            st.warning(f"No data vs {batter_hand}HH batters.")

    st.markdown("---")

    # Batter analysis
    st.header("Batter Analysis")

    # Get batted ball data
    batter_bip = batter_df[batter_df['launch_speed'].notna()]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Overall Stats")

        # Calculate batting stats
        hits = len(batter_df[batter_df['events'].isin(['single', 'double', 'triple', 'home_run'])])
        abs = len(batter_df[batter_df['events'].notna()])
        avg = hits / abs if abs > 0 else 0

        total_bases = (
            len(batter_df[batter_df['events'] == 'single']) +
            2 * len(batter_df[batter_df['events'] == 'double']) +
            3 * len(batter_df[batter_df['events'] == 'triple']) +
            4 * len(batter_df[batter_df['events'] == 'home_run'])
        )
        slg = total_bases / abs if abs > 0 else 0

        avg_xwoba = batter_bip['estimated_woba_using_speedangle'].mean() if len(batter_bip) > 0 else 0

        st.metric("Batting Avg", f"{avg:.3f}")
        st.metric("Slugging", f"{slg:.3f}")
        st.metric("xwOBA", f"{avg_xwoba:.3f}")

    with col2:
        st.subheader("Batted Ball")

        if len(batter_bip) > 0:
            avg_ev = batter_bip['launch_speed'].mean()
            max_ev = batter_bip['launch_speed'].max()
            avg_la = batter_bip['launch_angle'].mean()

            st.metric("Avg Exit Velo", f"{avg_ev:.1f} mph")
            st.metric("Max Exit Velo", f"{max_ev:.1f} mph")
            st.metric("Avg Launch Angle", f"{avg_la:.1f}°")
        else:
            st.warning("No batted ball data.")

    with col3:
        st.subheader("By Pitch Type")

        # Show xwOBA by pitch type (top 3)
        pitch_stats = batter_bip.groupby('pitch_name').agg({
            'estimated_woba_using_speedangle': 'mean',
            'launch_speed': 'count'
        }).reset_index()
        pitch_stats.columns = ['pitch_name', 'xwoba', 'count']
        pitch_stats = pitch_stats[pitch_stats['count'] >= 5]  # At least 5 BIP
        pitch_stats = pitch_stats.sort_values('xwoba', ascending=False).head(3)

        if len(pitch_stats) > 0:
            for _, row in pitch_stats.iterrows():
                st.metric(
                    row['pitch_name'],
                    f"{row['xwoba']:.3f} xwOBA",
                    delta=f"{int(row['count'])} BIP"
                )
        else:
            st.warning("Insufficient data by pitch type.")

else:
    st.info("Select a batter and pitcher to view matchup analysis.")
