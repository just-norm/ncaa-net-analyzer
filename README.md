# NCAA NET Rankings Analyzer

A comprehensive tool for analyzing NCAA Men's Basketball NET rankings and team schedules. Scrapes data from multiple ranking systems (NET, AP Poll, Coaches Poll, KenPom, Torvik, EvanMiya) and generates detailed quadrant analysis and interactive HTML dashboards.

## Features

- **Multi-Source Rankings**: Scrapes from NET, AP, Coaches, KenPom, Torvik, and EvanMiya
- **Quadrant Analysis**: Automatically categorizes games by NCAA quadrant definitions
- **Schedule Breakdown**: Analyzes wins/losses by quadrant and location (Home/Away/Neutral)
- **Interactive Dashboards**: Generates beautiful HTML dashboards for team resume analysis
- **Team Comparison**: Compare multiple teams' resumes and rankings

## Project Structure

```
ncaa_net_analyzer/
├── README.md
├── requirements.txt
├── analyzers/              # Analysis modules
│   ├── ncaa_net_analyzer.py    # Multi-ranking analyzer
│   └── arizona_net_analyzer.py # Arizona-specific analyzer
├── scrapers/               # Web scraping modules
│   ├── bballnet_scraper.py     # BBallNet.com scraper
│   └── team_scraper.py         # Generic team scraper
├── generators/             # Dashboard generators
│   ├── dashboard_generator.py          # Base dashboard generator
│   ├── michigan_dashboard_generator.py # Michigan dashboard
│   └── arizona_dashboard_generator.py  # Arizona dashboard
├── utils/                  # Utility functions
├── scripts/                # CLI tools
│   └── scrape_team.py      # Team data scraper CLI
└── data/                   # Generated data and outputs
    └── teams/
        ├── michigan/       # Michigan data files
        └── arizona/        # Arizona data files
```

## Quadrant Definitions

The NCAA uses NET rankings and game location to categorize games into quadrants:

- **Q1**: Home vs 1-30, Neutral vs 1-50, Away vs 1-75
- **Q2**: Home vs 31-75, Neutral vs 51-100, Away vs 76-135
- **Q3**: Home vs 76-160, Neutral vs 101-200, Away vs 136-240
- **Q4**: All other games

## Installation

```bash
# Clone the repository
cd ncaa_net_analyzer

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Scrape Team Data

```bash
# Scrape data for any team from bballnet.com
python scripts/scrape_team.py michigan
python scripts/scrape_team.py arizona
```

### Run Full Analysis

```bash
# Analyze with multiple ranking systems
python analyzers/ncaa_net_analyzer.py

# Analyze specific team
python analyzers/arizona_net_analyzer.py
```

### Generate Dashboard

```bash
# Generate interactive HTML dashboard
python generators/michigan_dashboard_generator.py
python generators/arizona_dashboard_generator.py
```

## Data Sources

- **NET Rankings**: NCAA.com
- **AP Poll**: NCAA.com
- **Coaches Poll**: NCAA.com (USA Today)
- **KenPom**: KenPom.com
- **Torvik (T-Rank)**: Barttorvik.com
- **EvanMiya**: EvanMiya.com
- **Schedule Data**: BBallNet.com

## Output Files

For each team analyzed, the following files are generated in `data/teams/<team_name>/`:

- `<team>_schedule_analysis.csv` - Full schedule with NET ranks and quadrants
- `<team>_own_rankings.csv` - Team's rankings across all systems
- `<team>_location_breakdown.csv` - Win statistics by quadrant and location
- `<team>_dashboard.html` - Interactive resume analysis dashboard

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml (optional, for faster parsing)

## Features in Detail

### Multi-Ranking Analysis
Combines rankings from 6 different systems to provide a composite view of team strength and opponent quality.

### Quadrant Tracking
Automatically categorizes each game based on opponent NET rank and game location according to NCAA selection committee criteria.

### Location Breakdown
Analyzes performance separately for home games, road games, and neutral site games within each quadrant.

### Dashboard Visualization
Beautiful, interactive HTML dashboards with:
- Quadrant win summaries
- Average and median NET rankings
- Full schedule breakdown
- Resume highlights
- Upcoming game opportunities

## Team Name Matching

The analyzer includes intelligent team name matching to handle variations across different data sources (e.g., "Michigan State" vs "Michigan St.").

## Notes

- Web scraping may fail if site structures change
- Some ranking systems may require authentication or have rate limits
- Generated dashboards work in any modern web browser
- Data is timestamped for tracking changes over the season

## License

This project is for educational and personal use. Please respect the terms of service of all data sources.

## Contributing

Feel free to submit issues or pull requests for improvements!
