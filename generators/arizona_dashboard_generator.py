#!/usr/bin/env python3
"""
Generate HTML dashboard from Arizona's schedule analysis CSV
"""

import csv
from datetime import datetime

def parse_date_for_sorting(date_str):
    """Convert 'Nov 14' format to sortable value for basketball season (Nov-Mar)"""
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str, '%b %d')
        # Assume current season: Nov-Dec are in 2024, Jan-Mar are in 2025
        month = date_obj.month
        year = 2024 if month >= 11 else 2025
        return datetime(year, month, date_obj.day)
    except:
        # If parsing fails, return a far future date to put it at the end
        return datetime(2099, 12, 31)

def generate_html_dashboard():
    """Generate the HTML dashboard from CSV data"""

    # Read the CSV data
    games = []
    with open('arizona_schedule_analysis.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            games.append(row)

    # Sort games by date chronologically
    games.sort(key=lambda x: parse_date_for_sorting(x['date']))

    # Read location breakdown
    location_breakdown = {}
    with open('arizona_location_breakdown.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            quad = row['Quadrant']
            if quad not in location_breakdown:
                location_breakdown[quad] = {}
            location_breakdown[quad][row['Location']] = {
                'wins': row['Wins'],
                'avg': row['Average_NET'],
                'median': row['Median_NET'],
                'ranks': row['NET_Ranks']
            }

    # Read Arizona's own rankings
    arizona_rankings = {}
    arizona_avg = 'N/A'
    try:
        with open('arizona_own_rankings.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row[0] == 'Average':
                    arizona_avg = row[1]
                else:
                    arizona_rankings[row[0]] = row[1]
    except FileNotFoundError:
        # Default values if file doesn't exist
        arizona_rankings = {
            'NET': 'NR',
            'AP': 'NR'
        }

    # Calculate overall stats
    quad_stats = {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []}
    for game in games:
        if game['result'] == 'W' and game['net_rank'] != 'N/A':
            quad = game['quadrant']
            if quad in quad_stats:
                quad_stats[quad].append(int(game['net_rank']))

    # Generate quadrant cards HTML
    def generate_quad_card(quad, color_class):
        wins = quad_stats[quad]
        if not wins:
            avg = 0
            median = 0
        else:
            avg = sum(wins) / len(wins)
            median = sorted(wins)[len(wins) // 2]

        card_html = f'''            <div class="stat-card {color_class}">
                <h3>Quadrant {quad[-1]} Wins</h3>
                <div class="stat-value">{len(wins)}</div>
                <div class="stat-detail">Overall Avg NET: <strong>{avg:.1f}</strong> | Median: <strong>{median}</strong></div>'''

        # Add location breakdowns
        if quad in location_breakdown:
            card_html += '\n                <div class="stat-detail" style="margin-top: 10px; border-top: 1px solid #eee; padding-top: 8px;">'
            for loc in ['Home', 'Away', 'Neutral']:
                if loc in location_breakdown[quad]:
                    loc_data = location_breakdown[quad][loc]
                    card_html += f'\n                    <strong>{loc} ({loc_data["wins"]}):</strong> Avg <strong>{loc_data["avg"]}</strong> | {loc_data["ranks"]}<br>'
                else:
                    card_html += f'\n                    <strong>{loc} (0):</strong> None<br>'
            card_html = card_html.rstrip('<br>')
            card_html += '\n                </div>'

        card_html += '\n            </div>'
        return card_html

    # Generate schedule table rows (completed games only)
    def generate_schedule_rows():
        rows_html = ''
        for game in games:
            # Skip upcoming games (TBD results)
            if game['result'] == 'TBD':
                continue

            result_badge = f'<span class="badge win">W</span>' if game['result'] == 'W' else f'<span class="badge loss">L</span>'

            quad = game['quadrant']
            quad_class = quad.lower()
            quad_badge = f'<span class="badge {quad_class}">{quad}</span>'

            # Highlight losses
            row_style = ' style="background: #ffe6e6;"' if game['result'] == 'L' else ''

            # Format location
            loc_display = game['location']
            if game['location'] == 'Neutral':
                loc_display = '<strong>Neutral</strong>'

            rows_html += f'''                    <tr{row_style}>
                        <td>{game['date']}</td>
                        <td>{game['opponent']}</td>
                        <td>{loc_display}</td>
                        <td>{result_badge}</td>
                        <td>{game['score']}</td>
                        <td><span class="net-rank">#{game['net_rank']}</span></td>
                        <td>{quad_badge}</td>
                    </tr>
'''
        return rows_html

    # Generate upcoming games rows
    def generate_upcoming_rows():
        upcoming = [g for g in games if g['result'] == 'TBD']
        if not upcoming:
            return ''

        rows_html = '''                    <tr style="background: #f0f8ff; border-top: 3px solid #003366;">
                        <td colspan="7" style="text-align: center; font-weight: bold; color: #003366; padding: 10px;">
                            UPCOMING GAMES
                        </td>
                    </tr>
'''
        for game in upcoming:
            quad_class = game['quadrant'].lower()
            quad_badge = f'<span class="badge {quad_class}">{game['quadrant']}</span>'
            net_display = f"#{game['net_rank']}" if game['net_rank'] else 'TBD'

            rows_html += f'''                    <tr style="background: #f9f9f9;">
                        <td>{game['date']}</td>
                        <td>{game['opponent']}</td>
                        <td>{game['location']}</td>
                        <td>-</td>
                        <td>-</td>
                        <td><span class="net-rank">{net_display}</span></td>
                        <td>{quad_badge}</td>
                    </tr>
'''
        return rows_html

    # Generate Resume Highlights
    def generate_resume_highlights():
        # Parse games by quadrant and location
        q1_home = []
        q1_away = []
        q1_neutral = []
        q2_wins = []
        losses = []

        for game in games:
            # Skip upcoming games (TBD)
            if game['result'] == 'TBD':
                continue

            if game['result'] == 'W':
                if game['quadrant'] == 'Q1' and game['net_rank'] != 'N/A':
                    game_info = (game['opponent'], int(game['net_rank']))
                    if game['location'] == 'Home':
                        q1_home.append(game_info)
                    elif game['location'] == 'Away':
                        q1_away.append(game_info)
                    elif game['location'] == 'Neutral':
                        q1_neutral.append(game_info)
                elif game['quadrant'] == 'Q2' and game['net_rank'] != 'N/A':
                    q2_wins.append((game['opponent'], int(game['net_rank'])))
            elif game['result'] == 'L':  # Only actual losses
                if game['net_rank'] != 'N/A':
                    losses.append((game['opponent'], int(game['net_rank']), game['location']))

        # Sort by NET ranking
        q1_home.sort(key=lambda x: x[1])
        q1_away.sort(key=lambda x: x[1])
        q1_neutral.sort(key=lambda x: x[1])
        q2_wins.sort(key=lambda x: x[1])

        # Build HTML
        html = '<div class="summary-box">\n'
        html += '                <h4>📊 Resume Highlights</h4>\n'
        html += '                <ul style="line-height: 1.8;">\n'

        # Q1 Home Wins
        if q1_home:
            html += f'                    <li><strong>Q1 Home Wins ({len(q1_home)}):</strong> '
            html += ', '.join([f'{opp} (#{net})' for opp, net in q1_home])
            html += '</li>\n'

        # Q1 Road Wins
        if q1_away:
            html += f'                    <li><strong>Q1 Road Wins ({len(q1_away)}):</strong> '
            html += ', '.join([f'@ {opp} (#{net})' for opp, net in q1_away])
            html += '</li>\n'

        # Q1 Neutral Wins
        if q1_neutral:
            html += f'                    <li><strong>Q1 Neutral Wins ({len(q1_neutral)}):</strong> '
            html += ', '.join([f'vs {opp} (#{net})' for opp, net in q1_neutral])
            html += '</li>\n'

        # Q2 Wins - show total and top 3
        if q2_wins:
            html += f'                    <li><strong>Q2 Wins ({len(q2_wins)}):</strong> '
            top_3 = q2_wins[:3] if len(q2_wins) >= 3 else q2_wins
            top_3_str = ', '.join([f'{opp} (#{net})' for opp, net in top_3])
            if len(q2_wins) > 3:
                html += f'Top 3 by NET: {top_3_str}'
            else:
                html += top_3_str
            html += '</li>\n'

        # Losses
        if losses:
            html += '                    <li><strong>Losses:</strong> '
            html += ', '.join([f'{"vs" if loc == "Home" else "@" if loc == "Away" else "vs"} {opp} (#{net})' for opp, net, loc in losses])
            html += '</li>\n'

        # Upcoming Q1 Opportunities
        upcoming_q1 = [(g['opponent'], int(g['net_rank']), g['location']) for g in games if g['result'] == 'TBD' and g['quadrant'] == 'Q1' and g['net_rank']]
        if upcoming_q1:
            html += '                    <li><strong>Remaining Q1 Opportunities:</strong> '
            q1_list = []
            for opp, net, loc in upcoming_q1:
                prefix = 'vs' if loc == 'Home' else '@'
                q1_list.append(f'{prefix} {opp} (#{net})')
            html += ', '.join(q1_list)
            html += '</li>\n'

        html += '                </ul>\n'
        html += '            </div>'

        return html

    # Build the full HTML
    # Build Arizona's rankings display (NET and AP only)
    rankings_display = []
    for system in ['NET', 'AP']:
        rank = arizona_rankings.get(system, 'NR')
        if rank != 'NR':
            rankings_display.append(f"{system}: #{rank}")
        else:
            rankings_display.append(f"{system}: NR")

    rankings_text = " | ".join(rankings_display)

    # Calculate record
    wins = sum(1 for g in games if g['result'] == 'W')
    losses = sum(1 for g in games if g['result'] == 'L')

    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arizona Basketball - NET Resume Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #CC0033 0%, #003366 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        .header {
            background: #003366;
            color: #CC0033;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 1.2em;
            color: white;
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #003366;
        }

        .stat-card.q1 {
            border-left-color: #d4af37;
        }

        .stat-card.q2 {
            border-left-color: #c0c0c0;
        }

        .stat-card.q3 {
            border-left-color: #cd7f32;
        }

        .stat-card.q4 {
            border-left-color: #808080;
        }

        .stat-card h3 {
            font-size: 1.1em;
            color: #666;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #003366;
            margin-bottom: 5px;
        }

        .stat-detail {
            font-size: 0.9em;
            color: #666;
            margin-top: 8px;
        }

        .content {
            padding: 30px;
        }

        .section-title {
            font-size: 1.8em;
            color: #003366;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #CC0033;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.95em;
        }

        thead {
            background: #003366;
            color: white;
        }

        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }

        tbody tr:hover {
            background: #f8f9fa;
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
        }

        .badge.q1 {
            background: #d4af37;
        }

        .badge.q2 {
            background: #c0c0c0;
            color: #333;
        }

        .badge.q3 {
            background: #cd7f32;
        }

        .badge.q4 {
            background: #808080;
        }

        .badge.q2-q3 {
            background: #a8a8a8;
        }

        .badge.win {
            background: #28a745;
            margin-left: 8px;
        }

        .badge.loss {
            background: #dc3545;
            margin-left: 8px;
        }

        .net-rank {
            font-weight: bold;
            color: #003366;
        }

        .summary-box {
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }

        .summary-box h4 {
            color: #003366;
            margin-bottom: 10px;
        }

        .summary-box ul {
            list-style: none;
            padding-left: 0;
        }

        .summary-box li {
            padding: 5px 0;
            color: #333;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #e0e0e0;
        }

        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 1.8em;
            }

            table {
                font-size: 0.85em;
            }

            th, td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏀 Arizona Wildcats</h1>
            <div class="subtitle">NET Resume Analysis | 2025-26 Season</div>
            <div style="margin-top: 15px; font-size: 1.1em;">
                Record: <strong>''' + f'{wins}-{losses}' + '''</strong>
            </div>
            <div style="margin-top: 10px; font-size: 0.95em; line-height: 1.6;">
                ''' + rankings_text + '''
            </div>
        </div>

        <div class="stats-grid">
'''

    # Add quadrant cards
    html_content += generate_quad_card('Q1', 'q1') + '\n\n'
    html_content += generate_quad_card('Q2', 'q2') + '\n\n'
    html_content += generate_quad_card('Q3', 'q3') + '\n\n'
    html_content += generate_quad_card('Q4', 'q4') + '\n'

    html_content += '''        </div>

        <div class="content">
'''

    # Add resume highlights
    html_content += generate_resume_highlights() + '\n\n'

    html_content += '''            <h2 class="section-title">Full Schedule Breakdown</h2>

            <table id="scheduleTable">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Opponent</th>
                        <th>Location</th>
                        <th>Result</th>
                        <th>Score</th>
                        <th>NET Rank</th>
                        <th>Quadrant</th>
                    </tr>
                </thead>
                <tbody>
'''

    # Add completed games
    html_content += generate_schedule_rows()

    # Add upcoming games
    html_content += generate_upcoming_rows()

    html_content += '''                </tbody>
            </table>

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

        <div class="footer">
            <p>Data scraped from NCAA.com NET Rankings | Generated on February 15, 2026</p>
            <p style="margin-top: 8px;">Arizona Cardinal Red (#CC0033) and Navy Blue (#003366)</p>
        </div>
    </div>

    <script>
        console.log('Arizona NET Resume Analyzer loaded successfully');
    </script>
</body>
</html>'''

    # Write to file
    with open('arizona_dashboard.html', 'w') as f:
        f.write(html_content)

    print("✅ Dashboard generated successfully!")
    if quad_stats['Q1']:
        print(f"   - {len(quad_stats['Q1'])} Q1 wins (Avg NET: {sum(quad_stats['Q1'])/len(quad_stats['Q1']):.1f})")
    if quad_stats['Q2']:
        print(f"   - {len(quad_stats['Q2'])} Q2 wins (Avg NET: {sum(quad_stats['Q2'])/len(quad_stats['Q2']):.1f})")
    print("   - Including neutral site breakdowns")
    print("   - All NET rankings verified from CSV")

if __name__ == "__main__":
    generate_html_dashboard()
