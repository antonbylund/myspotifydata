import json
import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import argparse

# Argument parser
parser = argparse.ArgumentParser(description='Explore Spotify Streaming History')
parser.add_argument('--top-artists', type=int, default=100, help='Number of top artists to display')
parser.add_argument('--top-tracks', type=int, default=100, help='Number of top tracks to display')
parser.add_argument('--top-genres', type=int, default=20, help='Number of top genres to display')
args = parser.parse_args()

# Path to extracted data
data_dir = Path(r"c:\Users\Anton\Desktop\spotifygrej\extracted\Spotify Extended Streaming History")
output_dir = Path(r"c:\Users\Anton\Desktop\spotifygrej\visualizations")
output_dir.mkdir(exist_ok=True)

# Load all streaming history JSON files
all_tracks = []
audio_files = sorted(data_dir.glob("Streaming_History_Audio_*.json"))

print(f"Found {len(audio_files)} audio streaming history files\n")

for file in audio_files:
    print(f"Loading {file.name}...")
    with open(file, 'r', encoding='utf-8') as f:
        tracks = json.load(f)
        all_tracks.extend(tracks)

print(f"\nTotal tracks loaded: {len(all_tracks)}\n")

# Create DataFrame
df = pd.DataFrame(all_tracks)

# Display basic stats
print("=" * 60)
print("SPOTIFY STREAMING DATA SUMMARY")
print("=" * 60)
print(f"\nDataFrame shape: {df.shape}")
print(f"Columns: {list(df.columns)}\n")

# Data types and missing values
print("Data Info:")
print(df.info())

# Basic statistics
print("\n" + "=" * 60)
print("STREAMING STATISTICS")
print("=" * 60)

# Convert ts to datetime
df['ts'] = pd.to_datetime(df['ts'])

print(f"\nDate range: {df['ts'].min()} to {df['ts'].max()}")
print(f"Total streaming time (hours): {df['ms_played'].sum() / 1000 / 60 / 60:.1f}")

# Top artists
print("\n" + "=" * 60)
print("TOP 10 ARTISTS")
print("=" * 60)
top_artists = df['master_metadata_album_artist_name'].value_counts().head(10)
for i, (artist, count) in enumerate(top_artists.items(), 1):
    print(f"{i}. {artist}: {count} streams")

# Top tracks
print("\n" + "=" * 60)
print("TOP 10 TRACKS")
print("=" * 60)
top_tracks = df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name']).size().sort_values(ascending=False).head(10)
for i, ((track, artist), count) in enumerate(top_tracks.items(), 1):
    print(f"{i}. {track} by {artist}: {count} streams")

# Streaming by year
print("\n" + "=" * 60)
print("STREAMS BY YEAR")
print("=" * 60)
df['year'] = df['ts'].dt.year
yearly_streams = df.groupby('year').size()
for year, count in yearly_streams.items():
    print(f"{year}: {count} streams")

# Tracks with actual listen time (ms > 0)
df_listened = df[df['ms_played'] > 0]
print(f"\nTracks actually listened to (ms_played > 0): {len(df_listened)} out of {len(df)}")
print(f"Average listen time: {df_listened['ms_played'].mean() / 1000:.1f} seconds")

print("\n" + "=" * 60)
print("Sample of your data:")
print("=" * 60)
print(df.head(10))

# =====================================================================
# CREATE INTERACTIVE VISUALIZATIONS
# =====================================================================
print("\n" + "=" * 60)
print("GENERATING INTERACTIVE VISUALIZATIONS")
print("=" * 60)

# 1. Top Artists - Interactive Bar Chart
fig1 = px.bar(
    top_artists.head(args.top_artists).reset_index(),
    x='count',
    y='master_metadata_album_artist_name',
    orientation='h',
    title=f'Top {args.top_artists} Artists by Stream Count',
    labels={'count': 'Number of Streams', 'master_metadata_album_artist_name': 'Artist'},
    color='count',
    color_continuous_scale='Viridis'
)
fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
fig1.write_html(output_dir / "01_top_artists.html")
print(f"✓ Saved: 01_top_artists.html")

# 2. Top Tracks - Interactive Bar Chart
top_tracks_df = df.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name']).size().reset_index(name='count').sort_values('count', ascending=False).head(args.top_tracks)
fig2 = px.bar(
    top_tracks_df,
    x='count',
    y='master_metadata_track_name',
    orientation='h',
    title=f'Top {args.top_tracks} Tracks by Stream Count',
    labels={'count': 'Number of Streams', 'master_metadata_track_name': 'Track'},
    color='count',
    color_continuous_scale='Plasma',
    hover_data={'master_metadata_album_artist_name': True}
)
fig2.update_layout(yaxis={'categoryorder': 'total ascending'}, height=min(1200, 30*args.top_tracks))
fig2.write_html(output_dir / "02_top_tracks.html")
print(f"✓ Saved: 02_top_tracks.html")

# 3. Streams by Year - Line Chart
yearly_data = df.groupby('year').size().reset_index(name='streams')
fig3 = px.line(
    yearly_data,
    x='year',
    y='streams',
    markers=True,
    title='Total Streams by Year',
    labels={'year': 'Year', 'streams': 'Number of Streams'},
    line_shape='linear'
)
fig3.update_traces(marker=dict(size=10), line=dict(width=3))
fig3.write_html(output_dir / "03_streams_by_year.html")
print("✓ Saved: 03_streams_by_year.html")

# 4. Streams by Month - Line Chart
df['year_month'] = df['ts'].dt.to_period('M')
monthly_data = df.groupby('year_month').size().reset_index(name='streams')
monthly_data['year_month'] = monthly_data['year_month'].astype(str)
fig4 = px.line(
    monthly_data,
    x='year_month',
    y='streams',
    title='Monthly Streaming Activity',
    labels={'year_month': 'Month', 'streams': 'Number of Streams'}
)
fig4.update_xaxes(tickangle=-45)
fig4.write_html(output_dir / "04_streams_by_month.html")
print("✓ Saved: 04_streams_by_month.html")

# 4.5. Streams by Day with 7-Day Moving Average (based on time listened)
df['date'] = df['ts'].dt.date
daily_data = df.groupby('date')['ms_played'].sum().reset_index(name='ms_played')
daily_data['date'] = pd.to_datetime(daily_data['date'])
daily_data = daily_data.sort_values('date')
# Convert milliseconds to hours
daily_data['hours_played'] = daily_data['ms_played'] / 1000 / 60 / 60
daily_data['moving_avg_7d'] = daily_data['hours_played'].rolling(window=7).mean()
daily_data['moving_avg_30d'] = daily_data['hours_played'].rolling(window=30).mean()
daily_data['moving_avg_365d'] = daily_data['hours_played'].rolling(window=365).mean()

fig4_5 = go.Figure()
# Add bars for daily hours listened
fig4_5.add_trace(go.Bar(
    x=daily_data['date'],
    y=daily_data['hours_played'],
    name='Hours Listened',
    marker_color='rgba(100, 150, 255, 0.6)',
    opacity=1
))
# Add line for 7-day moving average
fig4_5.add_trace(go.Scatter(
    x=daily_data['date'],
    y=daily_data['moving_avg_7d'],
    name='7-Day Moving Average',
    mode='lines',
    line=dict(color='red', width=3)
))
# Add line for 30-day moving average
fig4_5.add_trace(go.Scatter(
    x=daily_data['date'],
    y=daily_data['moving_avg_30d'],
    name='30-Day Moving Average',
    mode='lines',
    line=dict(color='green', width=3)
))
# Add line for 365-day moving average
fig4_5.add_trace(go.Scatter(
    x=daily_data['date'],
    y=daily_data['moving_avg_365d'],
    name='365-Day Moving Average',
    mode='lines',
    line=dict(color='orange', width=3)
))
fig4_5.update_layout(
    title='Daily Time Listened with 7-Day, 30-Day, and 365-Day Moving Averages',
    xaxis_title='Date',
    yaxis_title='Hours Listened',
    hovermode='x unified',
    height=500,
    yaxis=dict(range=[0, 24])
)
fig4_5.write_html(output_dir / "04b_streams_by_day_moving_avg.html")
print("✓ Saved: 04b_streams_by_day_moving_avg.html")

# 5. Streaming by Day of Week
df['day_of_week'] = df['ts'].dt.day_name()
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_data = df.groupby('day_of_week').size().reset_index(name='streams')
dow_data['day_of_week'] = pd.Categorical(dow_data['day_of_week'], categories=day_order, ordered=True)
dow_data = dow_data.sort_values('day_of_week')
fig5 = px.bar(
    dow_data,
    x='day_of_week',
    y='streams',
    title='Streams by Day of Week',
    labels={'day_of_week': 'Day of Week', 'streams': 'Number of Streams'},
    color='streams',
    color_continuous_scale='Blues'
)
fig5.write_html(output_dir / "05_streams_by_day_of_week.html")
print("✓ Saved: 05_streams_by_day_of_week.html")

# 6. Streaming by Hour of Day
df['hour'] = df['ts'].dt.hour
hourly_data = df.groupby('hour').size().reset_index(name='streams')
fig6 = px.bar(
    hourly_data,
    x='hour',
    y='streams',
    title='Streams by Hour of Day',
    labels={'hour': 'Hour of Day', 'streams': 'Number of Streams'},
    color='streams',
    color_continuous_scale='Greens'
)
fig6.update_xaxes(tickmode='linear', tick0=0, dtick=1)
fig6.write_html(output_dir / "06_streams_by_hour.html")
print("✓ Saved: 06_streams_by_hour.html")

# 7. Time Listened Distribution
df_listened = df[df['ms_played'] > 0].copy()
fig7 = px.histogram(
    df_listened,
    x='ms_played',
    nbins=100,
    title='Distribution of Time Listened per Track (seconds)',
    labels={'ms_played': 'Time Listened (milliseconds)'}
)
fig7.add_vline(x=df_listened['ms_played'].mean(), line_dash="dash", line_color="red", annotation_text="Mean")
fig7.write_html(output_dir / "07_time_listened_distribution.html")
print("✓ Saved: 07_time_listened_distribution.html")

# 8. Top Genres (inferred from artist frequency)
top_n_artists = df['master_metadata_album_artist_name'].value_counts().head(args.top_genres)
artist_genre_data = df[df['master_metadata_album_artist_name'].isin(top_n_artists.index)].groupby('master_metadata_album_artist_name').size().reset_index(name='streams')
fig8 = px.pie(
    artist_genre_data,
    values='streams',
    names='master_metadata_album_artist_name',
    title=f'Stream Distribution Among Top {args.top_genres} Artists',
    hole=0.3
)
fig8.write_html(output_dir / "08_artist_distribution_pie.html")
print("✓ Saved: 08_artist_distribution_pie.html")

# 9. Cumulative Streams Over Time
cumulative_data = df.sort_values('ts').reset_index(drop=True)
cumulative_data['cumulative_streams'] = range(1, len(cumulative_data) + 1)
cumulative_data_sample = cumulative_data.iloc[::100]  # Sample every 100th row for performance
fig9 = px.line(
    cumulative_data_sample,
    x='ts',
    y='cumulative_streams',
    title='Cumulative Streams Over Time',
    labels={'ts': 'Date', 'cumulative_streams': 'Cumulative Streams'}
)
fig9.update_xaxes(title_text="Date")
fig9.write_html(output_dir / "09_cumulative_streams.html")
print("✓ Saved: 09_cumulative_streams.html")

# 10. Heatmap: Streaming Activity by Day of Week and Hour
df['day_of_week_num'] = df['ts'].dt.dayofweek
heatmap_data = df.groupby(['day_of_week_num', 'hour']).size().reset_index(name='streams')
heatmap_pivot = heatmap_data.pivot(index='day_of_week_num', columns='hour', values='streams').fillna(0)
heatmap_pivot.index = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

fig10 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    colorscale='YlOrRd'
))
fig10.update_layout(
    title='Streaming Activity Heatmap (Day of Week vs Hour of Day)',
    xaxis_title='Hour of Day',
    yaxis_title='Day of Week',
    height=400
)
fig10.write_html(output_dir / "10_streaming_heatmap.html")
print("✓ Saved: 10_streaming_heatmap.html")

# 11. Top Artists - 2025 Only
df_2025 = df[df['year'] == 2025]
top_artists_2025 = df_2025['master_metadata_album_artist_name'].value_counts().head(args.top_artists)
fig11 = px.bar(
    top_artists_2025.reset_index(),
    x='count',
    y='master_metadata_album_artist_name',
    orientation='h',
    title=f'Top {args.top_artists} Artists in 2025 by Stream Count',
    labels={'count': 'Number of Streams', 'master_metadata_album_artist_name': 'Artist'},
    color='count',
    color_continuous_scale='Viridis'
)
fig11.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
fig11.write_html(output_dir / "11_top_artists_2025.html")
print(f"✓ Saved: 11_top_artists_2025.html")

# 12. Top Tracks - 2025 Only
top_tracks_2025_df = df_2025.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name']).size().reset_index(name='count').sort_values('count', ascending=False).head(args.top_tracks)
fig12 = px.bar(
    top_tracks_2025_df,
    x='count',
    y='master_metadata_track_name',
    orientation='h',
    title=f'Top {args.top_tracks} Tracks in 2025 by Stream Count',
    labels={'count': 'Number of Streams', 'master_metadata_track_name': 'Track'},
    color='count',
    color_continuous_scale='Plasma',
    hover_data={'master_metadata_album_artist_name': True}
)
fig12.update_layout(yaxis={'categoryorder': 'total ascending'}, height=min(1200, 30*args.top_tracks))
fig12.write_html(output_dir / "12_top_tracks_2025.html")
print(f"✓ Saved: 12_top_tracks_2025.html")

print("\n" + "=" * 60)
print(f"All visualizations saved to: {output_dir}")
print("=" * 60)
