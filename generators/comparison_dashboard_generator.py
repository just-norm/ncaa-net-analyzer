#!/usr/bin/env python3
"""
Generate comparison dashboard for two NCAA basketball teams
"""

import csv
import sys
from pathlib import Path

def load_team_data(team_name):
    """Load team data from CSV files"""
    team_dir = Path(f'../data/teams/{team_name.lower()}')

    # Load schedule
    schedule = []
    with open(team_dir / f'{team_name.lower()}_schedule_analysis.csv', 'r') as f:
        reader = csv.DictReader(f)
        schedule = list(reader)

    # Load rankings
    rankings = {}
    with open(team_dir / f'{team_name.lower()}_own_rankings.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            rankings[row[0]] = row[1]

    return {
        'name': team_name,
        'schedule': schedule,
        'rankings': rankings
    }

def calculate_stats(team_data):
    """Calculate team statistics"""
    stats = {
        'quad_records': {'Q1': {'W': 0, 'L': 0}, 'Q2': {'W': 0, 'L': 0},
                        'Q3': {'W': 0, 'L': 0}, 'Q4': {'W': 0, 'L': 0}},
        'quad_wins': {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []},
        'best_wins': [],
        'losses': [],
        'upcoming_q1': []
    }

    for game in team_data['schedule']:
        quad = game['quadrant']

        # Skip TBD games for records
        if game['result'] == 'TBD':
            if quad == 'Q1' and game['net_rank']:
                stats['upcoming_q1'].append((game['opponent'], int(game['net_rank']), game['location']))
            continue

        # Count wins/losses by quadrant
        if quad in stats['quad_records']:
            if game['result'] == 'W':
                stats['quad_records'][quad]['W'] += 1
                if game['net_rank']:
                    net_rank = int(game['net_rank'])
                    stats['quad_wins'][quad].append(net_rank)
                    stats['best_wins'].append((game['opponent'], net_rank, quad, game['location']))
            elif game['result'] == 'L':
                stats['quad_records'][quad]['L'] += 1
                if game['net_rank']:
                    stats['losses'].append((game['opponent'], int(game['net_rank']), quad))

    # Sort best wins by NET rank
    stats['best_wins'].sort(key=lambda x: x[1])

    # Calculate average NET by quadrant
    stats['quad_avg_net'] = {}
    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        if stats['quad_wins'][quad]:
            stats['quad_avg_net'][quad] = sum(stats['quad_wins'][quad]) / len(stats['quad_wins'][quad])
        else:
            stats['quad_avg_net'][quad] = None

    return stats

def generate_comparison_html(team1_data, team2_data, team1_stats, team2_stats):
    """Generate HTML comparison dashboard"""

    team1_name = team1_data['name']
    team2_name = team2_data['name']

    # Build quadrant comparison table
    quad_comparison = ''
    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        t1_record = team1_stats['quad_records'][quad]
        t2_record = team2_stats['quad_records'][quad]
        t1_wins = t1_record['W']
        t2_wins = t2_record['W']
        t1_avg = team1_stats['quad_avg_net'][quad]
        t2_avg = team2_stats['quad_avg_net'][quad]

        # Highlight advantage
        t1_style = 'font-weight: bold; color: #28a745;' if t1_wins > t2_wins else ''
        t2_style = 'font-weight: bold; color: #28a745;' if t2_wins > t1_wins else ''

        quad_comparison += f'''
                <tr>
                    <td><strong>{quad}</strong></td>
                    <td style="{t1_style}">{t1_wins}-{t1_record['L']}</td>
                    <td style="{t1_style}">{f"{t1_avg:.1f}" if t1_avg else "N/A"}</td>
                    <td style="{t2_style}">{t2_wins}-{t2_record['L']}</td>
                    <td style="{t2_style}">{f"{t2_avg:.1f}" if t2_avg else "N/A"}</td>
                </tr>'''

    # Build best wins comparison
    best_wins_html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">'

    # Team 1 best wins
    best_wins_html += f'''
        <div>
            <h4 style="color: #00274C; margin-bottom: 10px;">{team1_name} Top Wins</h4>
            <ul style="line-height: 1.8;">'''
    for opp, net, quad, loc in team1_stats['best_wins'][:10]:
        loc_prefix = 'vs' if loc == 'Home' else '@' if loc == 'Away' else 'vs'
        best_wins_html += f'<li><span class="badge {quad.lower()}">{quad}</span> {loc_prefix} {opp} (#{net})</li>'
    best_wins_html += '</ul></div>'

    # Team 2 best wins
    best_wins_html += f'''
        <div>
            <h4 style="color: #CC0033; margin-bottom: 10px;">{team2_name} Top Wins</h4>
            <ul style="line-height: 1.8;">'''
    for opp, net, quad, loc in team2_stats['best_wins'][:10]:
        loc_prefix = 'vs' if loc == 'Home' else '@' if loc == 'Away' else 'vs'
        best_wins_html += f'<li><span class="badge {quad.lower()}">{quad}</span> {loc_prefix} {opp} (#{net})</li>'
    best_wins_html += '</ul></div></div>'

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{team1_name} vs {team2_name} - Resume Comparison</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #00274C 0%, #CC0033 100%);
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
            background: linear-gradient(90deg, #00274C 0%, #CC0033 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .vs {{
            font-size: 1.5em;
            opacity: 0.9;
            margin: 0 20px;
        }}

        .rankings-bar {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            padding: 20px 30px;
            background: #f8f9fa;
            align-items: center;
        }}

        .team-ranking {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .team-ranking.team1 {{
            border-left: 4px solid #00274C;
        }}

        .team-ranking.team2 {{
            border-left: 4px solid #CC0033;
        }}

        .team-ranking h3 {{
            font-size: 1.1em;
            margin-bottom: 8px;
            color: #666;
        }}

        .team-ranking .rank {{
            font-size: 2em;
            font-weight: bold;
        }}

        .content {{
            padding: 30px;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #ddd;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        thead {{
            background: #f8f9fa;
        }}

        th {{
            padding: 12px;
            text-align: center;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
        }}

        td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #e0e0e0;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
            margin-right: 5px;
        }}

        .badge.q1 {{ background: #d4af37; }}
        .badge.q2 {{ background: #c0c0c0; color: #333; }}
        .badge.q3 {{ background: #cd7f32; }}
        .badge.q4 {{ background: #808080; }}

        .summary-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}

        .summary-box h4 {{
            color: #333;
            margin-bottom: 15px;
        }}

        .summary-box ul {{
            list-style: none;
            padding-left: 0;
        }}

        .summary-box li {{
            padding: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <span style="color: #FFCB05;">{team1_name}</span>
                <span class="vs">vs</span>
                <span style="color: #003366;">{team2_name}</span>
            </h1>
            <div style="margin-top: 10px; font-size: 1.1em;">Resume Comparison | 2025-26 Season</div>
        </div>

        <div class="rankings-bar">
            <div class="team-ranking team1">
                <h3>{team1_name} Rankings</h3>
                <div class="rank">NET: #{team1_data['rankings'].get('NET', 'NR')} | AP: #{team1_data['rankings'].get('AP', 'NR')}</div>
            </div>
            <div style="text-align: center; font-size: 2em; color: #666;">⚔️</div>
            <div class="team-ranking team2">
                <h3>{team2_name} Rankings</h3>
                <div class="rank">NET: #{team2_data['rankings'].get('NET', 'NR')} | AP: #{team2_data['rankings'].get('AP', 'NR')}</div>
            </div>
        </div>

        <div class="content">
            <h2 class="section-title">Quadrant Records Comparison</h2>
            <table>
                <thead>
                    <tr>
                        <th>Quadrant</th>
                        <th colspan="2">{team1_name}</th>
                        <th colspan="2">{team2_name}</th>
                    </tr>
                    <tr>
                        <th></th>
                        <th>Record</th>
                        <th>Avg NET</th>
                        <th>Record</th>
                        <th>Avg NET</th>
                    </tr>
                </thead>
                <tbody>
                    {quad_comparison}
                </tbody>
            </table>

            <h2 class="section-title">Quality Wins Breakdown</h2>
            <div class="summary-box">
                {best_wins_html}
            </div>

            <div class="summary-box" style="margin-top: 30px;">
                <h4>🎓 Understanding Quadrants</h4>
                <ul>
                    <li><strong>Q1:</strong> Home vs 1-30, Neutral vs 1-50, Away vs 1-75</li>
                    <li><strong>Q2:</strong> Home vs 31-75, Neutral vs 51-100, Away vs 76-135</li>
                    <li><strong>Q3:</strong> Home vs 76-160, Neutral vs 101-200, Away vs 136-240</li>
                    <li><strong>Q4:</strong> All other games</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>'''

    return html_content

def compare_teams(team1_name, team2_name):
    """Main comparison function"""
    print(f"🔍 Comparing {team1_name} vs {team2_name}...")

    # Load data
    team1_data = load_team_data(team1_name)
    team2_data = load_team_data(team2_name)

    # Calculate stats
    team1_stats = calculate_stats(team1_data)
    team2_stats = calculate_stats(team2_data)

    # Generate HTML
    html_content = generate_comparison_html(team1_data, team2_data, team1_stats, team2_stats)

    # Save
    output_file = f'comparison_{team1_name.lower()}_vs_{team2_name.lower()}.html'
    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"✅ Comparison dashboard saved to {output_file}")

    # Print summary
    print(f"\n📊 Comparison Summary:")
    print(f"\n{team1_name}:")
    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        rec = team1_stats['quad_records'][quad]
        print(f"  {quad}: {rec['W']}-{rec['L']}")

    print(f"\n{team2_name}:")
    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        rec = team2_stats['quad_records'][quad]
        print(f"  {quad}: {rec['W']}-{rec['L']}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python comparison_dashboard_generator.py <team1> <team2>")
        print("Example: python comparison_dashboard_generator.py Michigan Arizona")
        sys.exit(1)

    team1 = sys.argv[1]
    team2 = sys.argv[2]
    compare_teams(team1, team2)
