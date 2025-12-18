# Spotify Streaming History Analyzer

An interactive visualization tool for analyzing and exploring your Spotify streaming history using your personal data export.

## Features

- **12 Interactive Visualizations** using Plotly
- **Time-based Analysis** - View listening patterns by day, week, month, and year
- **Moving Averages** - 7-day, 30-day, and 365-day trend lines
- **Top Artists & Tracks** - Overall and year-specific rankings
- **Streaming Patterns** - Day of week and hour of day heatmaps
- **Customizable Output** - Command-line arguments to adjust visualization scope
- **2025-Only Analysis** - Special visualizations for current year data

## Requirements

- Python 3.11+
- pandas
- plotly
- numpy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spotify-analyzer.git
cd spotify-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Place your Spotify Extended Streaming History data:
   - Export your Spotify data from https://www.spotify.com/account/privacy/
   - Extract the zip file
   - Place the `Spotify Extended Streaming History` folder in `extracted/`

## Usage

### Basic Usage
```bash
python explore_spotify.py
```

This generates all 12 visualizations with default settings (top 100 artists/tracks).

### Custom Parameters
```bash
# Show top 50 artists and top 200 tracks
python explore_spotify.py --top-artists 50 --top-tracks 200

# Show top 30 artists for the pie chart
python explore_spotify.py --top-genres 30

# Combine all options
python explore_spotify.py --top-artists 200 --top-tracks 200 --top-genres 50
```

## Visualizations Generated

1. **01_top_artists.html** - Top 100 artists (all time)
2. **02_top_tracks.html** - Top 100 tracks (all time)
3. **03_streams_by_year.html** - Stream count by year
4. **04_streams_by_month.html** - Monthly streaming trends
5. **04b_streams_by_day_moving_avg.html** - Daily listening hours with moving averages
6. **05_streams_by_day_of_week.html** - Stream distribution by day
7. **06_streams_by_hour.html** - Stream distribution by hour of day
8. **07_time_listened_distribution.html** - Histogram of track listen times
9. **08_artist_distribution_pie.html** - Pie chart of top 20 artists
10. **09_cumulative_streams.html** - Cumulative streams over time
11. **10_streaming_heatmap.html** - Heatmap of streaming activity (day vs hour)
12. **11_top_artists_2025.html** - Top 100 artists (2025 only)
13. **12_top_tracks_2025.html** - Top 100 tracks (2025 only)

All visualizations are interactive HTML files that can be opened in any web browser.

## Data Privacy

This tool only analyzes data from your own Spotify export. No data is sent to external services. All visualizations are generated locally.

## File Structure

```
spotify-analyzer/
├── explore_spotify.py          # Main analysis script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .gitignore                   # Git ignore file
├── extracted/                   # Your Spotify data (not committed)
│   └── Spotify Extended Streaming History/
└── visualizations/              # Generated HTML visualizations (not committed)
    ├── 01_top_artists.html
    ├── 02_top_tracks.html
    └── ...
```

## Example Data Format

Your Spotify streaming history should be in the following structure:
```
extracted/
└── Spotify Extended Streaming History/
    ├── Streaming_History_Audio_2020-2022_0.json
    ├── Streaming_History_Audio_2022-2024_1.json
    ├── Streaming_History_Audio_2024-2025_5.json
    └── ...
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Notes

- The script processes all audio streaming history files in the data directory
- Missing data (null values) in the DataFrame is automatically handled
- The moving averages use backward-looking windows (previous data only)
- For daily listening analysis, the y-axis is fixed at 24 hours to represent a full day

## Contributing

Feel free to fork this project and submit pull requests with improvements!

## Author

Created for personal Spotify data analysis.
