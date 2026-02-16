#!/usr/bin/env python3
"""
Home page generator - displays all teams with NET rankings and stats
"""

import csv
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.team_config import load_teams


def load_team_summary(team_slug):
    """
    Load summary stats for a team

    Args:
        team_slug: Team slug

    Returns:
        dict: Team summary with NET rank, record, quad wins
    """
    team_dir = Path(__file__).parent.parent / 'data' / 'teams' / team_slug

    # Load rankings
    rankings_file = team_dir / f'{team_slug}_own_rankings.csv'
    net_rank = 'NR'
    ap_rank = 'NR'

    if rankings_file.exists():
        with open(rankings_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    if row[0] == 'NET':
                        net_rank = row[1]
                    elif row[0] == 'AP':
                        ap_rank = row[1]

    # Load schedule and calculate quad records
    schedule_file = team_dir / f'{team_slug}_schedule_analysis.csv'
    quad_records = {
        'Q1': {'W': 0, 'L': 0},
        'Q2': {'W': 0, 'L': 0},
        'Q3': {'W': 0, 'L': 0},
        'Q4': {'W': 0, 'L': 0}
    }
    total_wins = 0
    total_losses = 0

    if schedule_file.exists():
        with open(schedule_file, 'r') as f:
            reader = csv.DictReader(f)
            for game in reader:
                quad = game['quadrant']
                if game['result'] == 'W':
                    total_wins += 1
                    if quad in quad_records:
                        quad_records[quad]['W'] += 1
                elif game['result'] == 'L':
                    total_losses += 1
                    if quad in quad_records:
                        quad_records[quad]['L'] += 1

    record = f"{total_wins}-{total_losses}"

    return {
        'net_rank': net_rank,
        'ap_rank': ap_rank,
        'record': record,
        'quad_records': quad_records
    }


def generate_home_page(output_dir='public'):
    """
    Generate home page with all teams

    Args:
        output_dir: Output directory (default: 'public')
    """
    print("🏠 Generating home page...")

    # Load teams.json to get correct slugs
    teams_config_file = Path(__file__).parent.parent / 'config' / 'teams.json'
    team_slug_map = {}
    if teams_config_file.exists():
        with open(teams_config_file, 'r') as f:
            teams_config = json.load(f)
            for team in teams_config['teams']:
                team_slug_map[team['name']] = team['slug']

    # Load NET rankings (primary data source - has all 365 teams)
    net_rankings_file = Path(__file__).parent.parent / 'data' / 'net_rankings.csv'
    teams_data = []

    if net_rankings_file.exists():
        print("   Loading NET rankings from NCAA.com...")
        with open(net_rankings_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get team slug from teams.json config (correct slugs)
                team_name = row['Team']
                team_slug = team_slug_map.get(team_name, team_name.lower().replace(' ', '-').replace('.', '').replace("'", ''))

                # Load detailed stats if available
                summary = load_team_summary(team_slug)

                # Use NET rankings data as primary source
                teams_data.append({
                    'name': team_name,
                    'slug': team_slug,
                    'net_rank': row['Rank'],
                    'record': row['Record'],
                    'conference': row['Conference'],
                    'ap_rank': summary.get('ap_rank', 'NR'),
                    'quad_records': summary.get('quad_records', {
                        'Q1': {'W': 0, 'L': 0},
                        'Q2': {'W': 0, 'L': 0},
                        'Q3': {'W': 0, 'L': 0},
                        'Q4': {'W': 0, 'L': 0}
                    })
                })
        print(f"   ✅ Loaded {len(teams_data)} teams from NET rankings")
    else:
        # Fallback to teams.json (old behavior)
        print("   ⚠️  NET rankings file not found, using teams.json...")
        teams = load_teams()
        active_teams = [t for t in teams if t.get('active', True)]

        for team in active_teams:
            summary = load_team_summary(team['slug'])
            teams_data.append({
                'name': team['name'],
                'slug': team['slug'],
                'conference': team.get('conference', ''),
                **summary
            })

        # Sort by NET rank
        def sort_key(t):
            try:
                return (0, int(t['net_rank']))
            except (ValueError, TypeError):
                return (1, 999)

        teams_data.sort(key=sort_key)

    # Generate table rows
    table_rows = ''
    for idx, team in enumerate(teams_data, 1):
        net_display = f"#{team['net_rank']}" if team['net_rank'] != 'NR' else 'NR'
        ap_display = f"#{team['ap_rank']}" if team['ap_rank'] != 'NR' else 'NR'

        # Check if team has been scraped (has non-zero quad data)
        has_quad_data = any(
            team['quad_records'][q]['W'] + team['quad_records'][q]['L'] > 0
            for q in ['Q1', 'Q2', 'Q3', 'Q4']
        )

        # Format quad records as W-L or show "-" if not scraped
        if has_quad_data:
            q1_record = f"{team['quad_records']['Q1']['W']}-{team['quad_records']['Q1']['L']}"
            q2_record = f"{team['quad_records']['Q2']['W']}-{team['quad_records']['Q2']['L']}"
            q3_record = f"{team['quad_records']['Q3']['W']}-{team['quad_records']['Q3']['L']}"
            q4_record = f"{team['quad_records']['Q4']['W']}-{team['quad_records']['Q4']['L']}"
        else:
            q1_record = q2_record = q3_record = q4_record = '-'

        table_rows += f'''
            <tr>
                <td>{net_display}</td>
                <td>{ap_display}</td>
                <td><a href="/teams/{team['slug']}/" class="team-link">{team['name']}</a></td>
                <td>{team['conference']}</td>
                <td>{team['record']}</td>
                <td>{q1_record}</td>
                <td>{q2_record}</td>
                <td>{q3_record}</td>
                <td>{q4_record}</td>
            </tr>'''

    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCAA NET Rankings Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .controls {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }}

        .search-box {{
            width: 100%;
            max-width: 500px;
            padding: 12px 20px;
            font-size: 1em;
            border: 2px solid #ddd;
            border-radius: 8px;
            transition: border-color 0.3s;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #2a5298;
        }}

        .content {{
            padding: 30px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        thead {{
            background: #1e3c72;
            color: white;
            position: sticky;
            top: 0;
        }}

        th {{
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }}

        th:hover {{
            background: #2a5298;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .team-link {{
            color: #1e3c72;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s;
        }}

        .team-link:hover {{
            color: #2a5298;
            text-decoration: underline;
        }}

        .no-results {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏀 NCAA NET Rankings Dashboard</h1>
            <p>2025-26 Men's Basketball Season</p>
        </div>

        <div class="controls">
            <input type="text" id="searchBox" class="search-box" placeholder="🔍 Search teams...">
        </div>

        <div class="content">
            <table id="teamsTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">NET ↕</th>
                        <th onclick="sortTable(1)">AP ↕</th>
                        <th onclick="sortTable(2)">Team ↕</th>
                        <th onclick="sortTable(3)">Conference ↕</th>
                        <th onclick="sortTable(4)">Record ↕</th>
                        <th onclick="sortTable(5)">Q1 ↕</th>
                        <th onclick="sortTable(6)">Q2 ↕</th>
                        <th onclick="sortTable(7)">Q3 ↕</th>
                        <th onclick="sortTable(8)">Q4 ↕</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    {table_rows}
                </tbody>
            </table>

            <div id="noResults" class="no-results" style="display: none;">
                No teams found matching your search.
            </div>
        </div>
    </div>

    <script>
        // Search functionality
        const searchBox = document.getElementById('searchBox');
        const tableBody = document.getElementById('tableBody');
        const noResults = document.getElementById('noResults');
        const allRows = Array.from(tableBody.getElementsByTagName('tr'));

        searchBox.addEventListener('input', function(e) {{
            const searchTerm = e.target.value.toLowerCase();
            let visibleCount = 0;

            allRows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});

            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }});

        // Simple table sorting
        function sortTable(columnIndex) {{
            const rows = Array.from(tableBody.getElementsByTagName('tr'));
            // Columns 0 (NET), 1 (AP), 5-8 (Quad records) are numeric
            const isNumeric = columnIndex === 0 || columnIndex === 1 || columnIndex === 5 || columnIndex === 6 || columnIndex === 7 || columnIndex === 8;

            rows.sort((a, b) => {{
                let aVal = a.getElementsByTagName('td')[columnIndex].textContent;
                let bVal = b.getElementsByTagName('td')[columnIndex].textContent;

                if (isNumeric) {{
                    // For quad records (e.g., "9-0"), extract wins for sorting
                    if (columnIndex >= 5) {{
                        aVal = aVal.split('-')[0] || '0';
                        bVal = bVal.split('-')[0] || '0';
                    }} else {{
                        // For NET/AP ranks, extract numbers, treat NR as very high
                        aVal = aVal.replace(/[^0-9]/g, '') || '999';
                        bVal = bVal.replace(/[^0-9]/g, '') || '999';
                    }}
                    return parseInt(bVal) - parseInt(aVal); // Descending for wins
                }} else {{
                    return aVal.localeCompare(bVal);
                }}
            }});

            rows.forEach(row => tableBody.appendChild(row));
        }}
    </script>
</body>
</html>'''

    # Write to output file
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / 'index.html'

    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"✅ Home page generated: {output_file}")
    return True


if __name__ == "__main__":
    generate_home_page()
