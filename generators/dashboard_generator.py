#!/usr/bin/env python3
"""
Unified dashboard generator for NCAA basketball teams
Generates HTML dashboards for any team using configuration files
"""

import csv
import sys
from pathlib import Path
from datetime import datetime

# Import utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.team_config import get_team_by_slug, get_team_colors
from utils.date_utils import parse_game_date
from utils.quadrant_calculator import calculate_quadrant


def load_team_data(team_slug):
    """Load team data from CSV files"""
    team_dir = Path(__file__).parent.parent / 'data' / 'teams' / team_slug

    # Load schedule
    schedule_file = team_dir / f'{team_slug}_schedule_analysis.csv'
    games = []

    if schedule_file.exists():
        with open(schedule_file, 'r') as f:
            reader = csv.DictReader(f)
            games = list(reader)

    # Load rankings
    rankings_file = team_dir / f'{team_slug}_own_rankings.csv'
    rankings = {}

    if rankings_file.exists():
        with open(rankings_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    rankings[row[0]] = row[1]

    return {
        'games': games,
        'rankings': rankings
    }


def calculate_team_stats(games, conference=''):
    """Calculate team statistics from schedule"""
    stats = {
        'quad_records': {'Q1': {'W': 0, 'L': 0}, 'Q2': {'W': 0, 'L': 0},
                        'Q3': {'W': 0, 'L': 0}, 'Q4': {'W': 0, 'L': 0}},
        'quad_wins': {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []},
        'q1_by_location': {'Home': [], 'Away': [], 'Neutral': []},
        'q2_wins': [],
        'best_wins': [],
        'losses': [],
        'upcoming_q1': [],
        'total_wins': 0,
        'total_losses': 0,
        'conference_wins': 0,
        'conference_losses': 0
    }

    # Conference team mapping (simplified - checking if opponent contains conference name keywords)
    conference_keywords = {
        'Big Ten': ['Michigan', 'Ohio State', 'Penn State', 'Wisconsin', 'Indiana', 'Nebraska',
                    'Iowa', 'Illinois', 'Northwestern', 'Purdue', 'Minnesota', 'Rutgers',
                    'Michigan State', 'Maryland', 'Oregon', 'Washington', 'UCLA', 'USC', 'Southern California'],
        'ACC': ['Duke', 'North Carolina', 'Virginia', 'Miami', 'Clemson', 'NC State',
                'Virginia Tech', 'Wake Forest', 'Louisville', 'Florida State', 'Syracuse',
                'Pittsburgh', 'Boston College', 'Georgia Tech', 'Notre Dame', 'Stanford', 'California'],
        'Big 12': ['Kansas', 'Baylor', 'Texas Tech', 'Iowa State', 'Kansas State', 'TCU',
                   'West Virginia', 'Oklahoma State', 'Texas', 'Oklahoma', 'Arizona', 'Arizona State',
                   'Colorado', 'Utah', 'BYU', 'Cincinnati', 'Houston', 'UCF'],
        'SEC': ['Auburn', 'Kentucky', 'Tennessee', 'Alabama', 'Arkansas', 'Florida',
                'LSU', 'Mississippi State', 'Ole Miss', 'Georgia', 'South Carolina',
                'Missouri', 'Texas A&M', 'Vanderbilt'],
        'Big East': ['UConn', 'Villanova', 'Marquette', 'Creighton', 'Providence',
                     'Xavier', 'Butler', 'Seton Hall', 'St. John\'s', 'Georgetown', 'DePaul']
    }

    for game in games:
        quad = game['quadrant']
        result = game['result']
        opponent = game.get('opponent', '')

        # Check if conference game
        is_conference_game = False
        if conference and conference in conference_keywords:
            conf_teams = conference_keywords[conference]
            is_conference_game = any(team_name in opponent for team_name in conf_teams)

        # Skip TBD games for records
        if result == 'TBD':
            if quad == 'Q1' and game.get('net_rank'):
                try:
                    stats['upcoming_q1'].append((
                        game['opponent'],
                        int(game['net_rank']),
                        game['location']
                    ))
                except (ValueError, KeyError):
                    pass
            continue

        # Count wins/losses by quadrant
        if quad in stats['quad_records']:
            if result == 'W':
                stats['quad_records'][quad]['W'] += 1
                stats['total_wins'] += 1
                if is_conference_game:
                    stats['conference_wins'] += 1
                if game.get('net_rank') and game['net_rank'] not in ['', 'NR', 'N/A']:
                    try:
                        net_rank = int(game['net_rank'])
                        stats['quad_wins'][quad].append(net_rank)
                        stats['best_wins'].append((
                            game['opponent'],
                            net_rank,
                            quad,
                            game['location']
                        ))

                        # Track Q1 wins by location
                        if quad == 'Q1':
                            location = game['location']
                            if location in stats['q1_by_location']:
                                stats['q1_by_location'][location].append((
                                    game['opponent'],
                                    net_rank
                                ))

                        # Track Q2 wins
                        if quad == 'Q2':
                            stats['q2_wins'].append((
                                game['opponent'],
                                net_rank,
                                game['location']
                            ))
                    except ValueError:
                        pass
            elif result == 'L':
                stats['quad_records'][quad]['L'] += 1
                stats['total_losses'] += 1
                if is_conference_game:
                    stats['conference_losses'] += 1
                if game.get('net_rank') and game['net_rank'] not in ['', 'NR', 'N/A']:
                    try:
                        stats['losses'].append((
                            game['opponent'],
                            int(game['net_rank']),
                            quad,
                            game['location']
                        ))
                    except ValueError:
                        pass

    # Sort best wins by NET rank
    stats['best_wins'].sort(key=lambda x: x[1])

    return stats


def generate_team_dashboard(team_slug, output_dir='public'):
    """
    Generate HTML dashboard for a team

    Args:
        team_slug: Team slug (e.g., 'michigan', 'duke')
        output_dir: Output directory (default: 'public')
    """
    # Load team config and colors
    team = get_team_by_slug(team_slug)
    if not team:
        print(f"❌ Team '{team_slug}' not found in configuration")
        return False

    colors = get_team_colors(team_slug)
    team_name = team['name']
    conference = team.get('conference', '')

    # Load data
    data = load_team_data(team_slug)
    games = data['games']
    rankings = data['rankings']

    if not games:
        print(f"⚠️  No schedule data found for {team_name}")
        return False

    # Sort games chronologically
    games.sort(key=lambda x: parse_game_date(x['date']))

    # Calculate stats
    stats = calculate_team_stats(games, conference)

    # Get rankings
    net_rank = rankings.get('NET', 'NR')
    ap_rank = rankings.get('AP', 'NR')

    # Calculate record
    record = f"{stats['total_wins']}-{stats['total_losses']}"
    conference_record = f"{stats['conference_wins']}-{stats['conference_losses']}"

    # Generate HTML sections
    schedule_html = generate_schedule_html(games, colors)
    quad_cards_html = generate_quad_cards_html(stats)
    resume_highlights_html = generate_resume_highlights_html(stats, colors)

    # Generate complete HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{team_name} Basketball - NET Rankings Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            color: {colors['name_color']};
        }}

        .rankings-bar {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
        }}

        .ranking {{
            background: rgba(255, 255, 255, 0.2);
            padding: 15px 30px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}

        .ranking-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .ranking-value {{
            font-size: 2em;
            font-weight: bold;
            margin-top: 5px;
        }}

        .content {{
            padding: 30px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid {colors['primary']};
        }}

        .quad-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            margin: -30px -30px 30px -30px;
        }}

        .quad-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid;
        }}

        .quad-card.q1 {{ border-left-color: #d4af37; }}
        .quad-card.q2 {{ border-left-color: #c0c0c0; }}
        .quad-card.q3 {{ border-left-color: #cd7f32; }}
        .quad-card.q4 {{ border-left-color: #808080; }}

        .quad-card h3 {{
            font-size: 1.1em;
            color: #666;
            margin-bottom: 10px;
        }}

        .quad-record {{
            font-size: 2.5em;
            font-weight: bold;
            color: {colors['primary']};
            margin-bottom: 5px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        thead {{
            background: {colors['primary']};
            color: white;
        }}

        th {{
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .win {{ background: #d4edda; }}
        .loss {{ background: #f8d7da; }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
        }}

        .badge.q1 {{ background: #d4af37; }}
        .badge.q2 {{ background: #c0c0c0; color: #333; }}
        .badge.q3 {{ background: #cd7f32; }}
        .badge.q4 {{ background: #808080; }}

        .net-rank {{
            background: {colors['primary']};
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}

        .highlights {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid {colors['primary']};
        }}

        .highlights ul {{
            list-style: none;
            padding-left: 0;
        }}

        .highlights li {{
            padding: 8px 0;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{team_name}</h1>
            <div style="font-size: 1.2em; margin: 10px 0;">Record: <strong>{record}</strong> ({conference_record} {conference})</div>
            <div class="rankings-bar">
                <div class="ranking">
                    <div class="ranking-label">NET Ranking</div>
                    <div class="ranking-value">#{net_rank}</div>
                </div>
                <div class="ranking">
                    <div class="ranking-label">AP Poll</div>
                    <div class="ranking-value">#{ap_rank}</div>
                </div>
            </div>
        </div>

        <div class="content">
            <div class="section">
                <h2 class="section-title">Quadrant Performance</h2>
                {quad_cards_html}
            </div>

            <div class="section">
                <h2 class="section-title">Resume Highlights</h2>
                {resume_highlights_html}
            </div>

            <div class="section">
                <h2 class="section-title">Full Schedule Breakdown</h2>
                {schedule_html}
            </div>
        </div>
    </div>
</body>
</html>'''

    # Write to output file
    output_path = Path(output_dir) / 'teams' / team_slug
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / 'index.html'

    with open(output_file, 'w') as f:
        f.write(html_content)

    return True


def generate_quad_cards_html(stats):
    """Generate quadrant cards HTML"""
    html = '<div class="quad-grid">'

    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        record = stats['quad_records'][quad]
        wins = record['W']
        losses = record['L']

        # Calculate average and median NET for wins in this quadrant
        quad_net_ranks = stats['quad_wins'][quad]
        avg_net = ''
        median_net = ''

        if quad_net_ranks:
            avg_net = f"{sum(quad_net_ranks) / len(quad_net_ranks):.1f}"
            sorted_ranks = sorted(quad_net_ranks)
            mid = len(sorted_ranks) // 2
            if len(sorted_ranks) % 2 == 0:
                median_net = f"{(sorted_ranks[mid-1] + sorted_ranks[mid]) / 2:.0f}"
            else:
                median_net = f"{sorted_ranks[mid]}"

        html += f'''
        <div class="quad-card {quad.lower()}">
            <h3>Quadrant {quad[1]} Wins</h3>
            <div class="quad-record">{wins}</div>'''

        if avg_net and median_net:
            html += f'''<div style="font-size: 0.9em; color: #666; margin-top: 8px;">
                NET Wins Avg: <strong>{avg_net}</strong>
            </div>
            <div style="font-size: 0.9em; color: #666; margin-top: 4px;">
                NET Wins Median: <strong>{median_net}</strong>
            </div>'''

        html += '</div>'

    html += '</div>'
    return html


def generate_schedule_html(games, colors):
    """Generate schedule table HTML"""
    html = '''<table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Opponent</th>
                <th>Location</th>
                <th>Result</th>
                <th>Score</th>
                <th>Opp NET</th>
                <th>Quadrant</th>
            </tr>
        </thead>
        <tbody>'''

    # Completed games
    for game in games:
        if game['result'] == 'TBD':
            continue

        row_class = 'win' if game['result'] == 'W' else 'loss'
        quad_class = game['quadrant'].lower()
        net_display = f"#{game['net_rank']}" if game.get('net_rank') and game['net_rank'] not in ['', 'NR', 'N/A'] else 'NR'

        html += f'''
            <tr class="{row_class}">
                <td>{game['date']}</td>
                <td>{game['opponent']}</td>
                <td>{game['location']}</td>
                <td><strong>{game['result']}</strong></td>
                <td>{game.get('score', '')}</td>
                <td><span class="net-rank">{net_display}</span></td>
                <td><span class="badge {quad_class}">{game['quadrant']}</span></td>
            </tr>'''

    # Upcoming games
    has_upcoming = any(g['result'] == 'TBD' for g in games)
    if has_upcoming:
        html += '''<tr style="background: #f0f8ff; border-top: 3px solid ''' + colors['primary'] + ''';">
                <td colspan="7" style="text-align: center; font-weight: bold; padding: 10px;">
                    UPCOMING GAMES
                </td>
            </tr>'''

        for game in games:
            if game['result'] != 'TBD':
                continue

            quad_class = game['quadrant'].lower()
            net_display = f"#{game['net_rank']}" if game.get('net_rank') and game['net_rank'] not in ['', 'NR', 'N/A'] else 'TBD'

            html += f'''
            <tr style="background: #f9f9f9;">
                <td>{game['date']}</td>
                <td>{game['opponent']}</td>
                <td>{game['location']}</td>
                <td>-</td>
                <td>-</td>
                <td><span class="net-rank">{net_display}</span></td>
                <td><span class="badge {quad_class}">{game['quadrant']}</span></td>
            </tr>'''

    html += '</tbody></table>'
    return html


def generate_resume_highlights_html(stats, colors):
    """Generate resume highlights section with detailed Q1 breakdown"""
    html = '<div class="highlights"><ul style="line-height: 1.8;">'

    # Q1 Home Wins
    q1_home = stats['q1_by_location']['Home']
    if q1_home:
        html += f'<li><strong>Q1 Home Wins ({len(q1_home)}):</strong> '
        wins_list = [f'{opp} (#{net})' for opp, net in q1_home]
        html += ', '.join(wins_list)
        html += '</li>'

    # Q1 Road Wins
    q1_away = stats['q1_by_location']['Away']
    if q1_away:
        html += f'<li><strong>Q1 Road Wins ({len(q1_away)}):</strong> '
        wins_list = [f'@ {opp} (#{net})' for opp, net in q1_away]
        html += ', '.join(wins_list)
        html += '</li>'

    # Q1 Neutral Wins
    q1_neutral = stats['q1_by_location']['Neutral']
    if q1_neutral:
        html += f'<li><strong>Q1 Neutral Wins ({len(q1_neutral)}):</strong> '
        wins_list = [f'vs {opp} (#{net})' for opp, net in q1_neutral]
        html += ', '.join(wins_list)
        html += '</li>'

    # Q2 Wins (Top 3 by NET)
    if stats['q2_wins']:
        q2_sorted = sorted(stats['q2_wins'], key=lambda x: x[1])[:3]
        html += f'<li><strong>Top Q2 Wins:</strong> '
        wins_list = []
        for opp, net, loc in q2_sorted:
            prefix = '@' if loc == 'Away' else 'vs'
            wins_list.append(f'{prefix} {opp} (#{net})')
        html += ', '.join(wins_list)
        html += '</li>'

    # Losses
    if stats['losses']:
        html += '<li><strong>Losses:</strong> '
        losses_list = []
        for opp, net, quad, loc in stats['losses']:
            prefix = '@' if loc == 'Away' else 'vs'
            losses_list.append(f'{prefix} {opp} (#{net})')
        html += ', '.join(losses_list)
        html += '</li>'

    # Upcoming Q1 opportunities
    if stats['upcoming_q1']:
        html += '<li><strong>Remaining Q1 Opportunities:</strong> '
        q1_list = []
        for opp, net, loc in stats['upcoming_q1']:
            prefix = '@' if loc == 'Away' else 'vs'
            q1_list.append(f'{prefix} {opp} (#{net})')
        html += ', '.join(q1_list)
        html += '</li>'

    html += '</ul></div>'
    return html


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dashboard_generator.py <team-slug>")
        print("Example: python dashboard_generator.py michigan")
        sys.exit(1)

    team_slug = sys.argv[1]
    success = generate_team_dashboard(team_slug)

    if success:
        print(f"✅ Dashboard generated for {team_slug}")
    else:
        print(f"❌ Failed to generate dashboard for {team_slug}")
        sys.exit(1)
