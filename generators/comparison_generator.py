#!/usr/bin/env python3
"""
Comparison tool generator - creates head-to-head team comparison page
"""

import csv
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_team_data(team_slug):
    """
    Load complete team data for comparison

    Args:
        team_slug: Team slug

    Returns:
        dict: Team data including rankings, schedule, quad records
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

    # Load schedule and analyze
    schedule_file = team_dir / f'{team_slug}_schedule_analysis.csv'
    quad_records = {
        'Q1': {'W': 0, 'L': 0},
        'Q2': {'W': 0, 'L': 0},
        'Q3': {'W': 0, 'L': 0},
        'Q4': {'W': 0, 'L': 0}
    }
    best_wins = []
    worst_losses = []
    total_wins = 0
    total_losses = 0

    if schedule_file.exists():
        with open(schedule_file, 'r') as f:
            reader = csv.DictReader(f)
            for game in reader:
                quad = game['quadrant']
                opponent = game['opponent']
                net_rank_opp = game.get('net_rank', 'NR')
                location = game['location']
                result = game['result']

                if result == 'W':
                    total_wins += 1
                    if quad in quad_records:
                        quad_records[quad]['W'] += 1

                    # Track best wins (Q1/Q2 wins with opponent NET rank)
                    if quad in ['Q1', 'Q2'] and net_rank_opp != 'NR':
                        try:
                            best_wins.append({
                                'opponent': opponent,
                                'net_rank': int(net_rank_opp),
                                'location': location,
                                'quad': quad
                            })
                        except ValueError:
                            pass

                elif result == 'L':
                    total_losses += 1
                    if quad in quad_records:
                        quad_records[quad]['L'] += 1

                    # Track worst losses (Q3/Q4 losses with opponent NET rank)
                    if quad in ['Q3', 'Q4'] and net_rank_opp != 'NR':
                        try:
                            worst_losses.append({
                                'opponent': opponent,
                                'net_rank': int(net_rank_opp),
                                'location': location,
                                'quad': quad
                            })
                        except ValueError:
                            pass

    # Sort best wins by opponent NET rank (lower is better)
    best_wins.sort(key=lambda x: x['net_rank'])
    # Sort worst losses by opponent NET rank (higher is worse)
    worst_losses.sort(key=lambda x: x['net_rank'], reverse=True)

    record = f"{total_wins}-{total_losses}"

    return {
        'slug': team_slug,
        'net_rank': net_rank,
        'ap_rank': ap_rank,
        'record': record,
        'quad_records': quad_records,
        'best_wins': best_wins[:5],  # Top 5 wins
        'worst_losses': worst_losses[:5]  # Top 5 worst losses
    }


def generate_comparison_page(output_dir='public'):
    """
    Generate comparison tool page

    Args:
        output_dir: Output directory (default: 'public')
    """
    print("⚔️  Generating comparison tool...")

    # Load all teams for autocomplete
    teams_config_file = Path(__file__).parent.parent / 'config' / 'teams.json'
    teams_list = []

    if teams_config_file.exists():
        with open(teams_config_file, 'r') as f:
            teams_config = json.load(f)
            teams_list = [{'name': t['name'], 'slug': t['slug']} for t in teams_config['teams']]

    # Convert teams to JSON for JavaScript
    teams_json = json.dumps(teams_list)

    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Comparison - NCAA NET Analyzer</title>
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

        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: white;
            text-decoration: none;
            opacity: 0.9;
        }}

        .back-link:hover {{
            opacity: 1;
            text-decoration: underline;
        }}

        .content {{
            padding: 30px;
        }}

        .team-selector {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            margin-bottom: 40px;
            align-items: center;
        }}

        .autocomplete-wrapper {{
            position: relative;
        }}

        .autocomplete-input {{
            width: 100%;
            padding: 12px 20px;
            font-size: 1.1em;
            border: 2px solid #ddd;
            border-radius: 8px;
            transition: border-color 0.3s;
        }}

        .autocomplete-input:focus {{
            outline: none;
            border-color: #2a5298;
        }}

        .autocomplete-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 2px solid #2a5298;
            border-top: none;
            border-radius: 0 0 8px 8px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }}

        .autocomplete-results.show {{
            display: block;
        }}

        .autocomplete-item {{
            padding: 12px 20px;
            cursor: pointer;
            transition: background 0.2s;
        }}

        .autocomplete-item:hover {{
            background: #f0f0f0;
        }}

        .vs-badge {{
            font-size: 2em;
            font-weight: bold;
            color: #666;
        }}

        .compare-button {{
            width: 100%;
            padding: 15px;
            font-size: 1.2em;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s;
        }}

        .compare-button:hover {{
            background: #1e3c72;
        }}

        .compare-button:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}

        .comparison-result {{
            display: none;
        }}

        .comparison-result.show {{
            display: block;
        }}

        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }}

        .team-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 25px;
        }}

        .team-card h2 {{
            color: #1e3c72;
            margin-bottom: 15px;
            font-size: 1.8em;
        }}

        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }}

        .stat-row:last-child {{
            border-bottom: none;
        }}

        .stat-label {{
            font-weight: 600;
            color: #666;
        }}

        .stat-value {{
            color: #1e3c72;
            font-weight: bold;
        }}

        .quad-comparison {{
            margin-top: 40px;
        }}

        .quad-comparison h3 {{
            color: #1e3c72;
            margin-bottom: 20px;
            text-align: center;
        }}

        .quad-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .quad-table th {{
            background: #1e3c72;
            color: white;
            padding: 12px;
            text-align: left;
        }}

        .quad-table td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}

        .quad-table tr:hover {{
            background: #f8f9fa;
        }}

        .wins-list {{
            margin-top: 30px;
        }}

        .wins-list h4 {{
            color: #1e3c72;
            margin-bottom: 15px;
        }}

        .win-item {{
            padding: 10px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-left: 4px solid #2a5298;
            border-radius: 4px;
        }}

        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}

        .empty-state h3 {{
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/" class="back-link">← Back to Rankings</a>
            <h1>⚔️ Team Comparison</h1>
            <p>Head-to-Head Resume Analysis</p>
        </div>

        <div class="content">
            <div class="team-selector">
                <div class="autocomplete-wrapper">
                    <input type="text"
                           id="team1Input"
                           class="autocomplete-input"
                           placeholder="Search for first team...">
                    <div id="team1Results" class="autocomplete-results"></div>
                </div>

                <div class="vs-badge">VS</div>

                <div class="autocomplete-wrapper">
                    <input type="text"
                           id="team2Input"
                           class="autocomplete-input"
                           placeholder="Search for second team...">
                    <div id="team2Results" class="autocomplete-results"></div>
                </div>
            </div>

            <button id="compareButton" class="compare-button" disabled>
                Select Two Teams to Compare
            </button>

            <div id="emptyState" class="empty-state">
                <h3>Select two teams to compare their resumes</h3>
                <p>Use the search boxes above to find teams by name</p>
            </div>

            <div id="comparisonResult" class="comparison-result">
                <!-- Comparison will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        const teams = {teams_json};
        let selectedTeam1 = null;
        let selectedTeam2 = null;

        // Autocomplete functionality
        function setupAutocomplete(inputId, resultsId, onSelect) {{
            const input = document.getElementById(inputId);
            const results = document.getElementById(resultsId);

            input.addEventListener('input', function(e) {{
                const searchTerm = e.target.value.toLowerCase();

                if (searchTerm.length < 2) {{
                    results.classList.remove('show');
                    return;
                }}

                const matches = teams.filter(team =>
                    team.name.toLowerCase().includes(searchTerm)
                ).slice(0, 10);

                if (matches.length > 0) {{
                    results.innerHTML = matches.map(team =>
                        `<div class="autocomplete-item" data-slug="${{team.slug}}" data-name="${{team.name}}">
                            ${{team.name}}
                        </div>`
                    ).join('');
                    results.classList.add('show');

                    // Add click handlers
                    results.querySelectorAll('.autocomplete-item').forEach(item => {{
                        item.addEventListener('click', function() {{
                            const teamSlug = this.dataset.slug;
                            const teamName = this.dataset.name;
                            input.value = teamName;
                            results.classList.remove('show');
                            onSelect(teamSlug, teamName);
                        }});
                    }});
                }} else {{
                    results.classList.remove('show');
                }}
            }});

            // Close results when clicking outside
            document.addEventListener('click', function(e) {{
                if (!input.contains(e.target) && !results.contains(e.target)) {{
                    results.classList.remove('show');
                }}
            }});
        }}

        // Setup both autocomplete inputs
        setupAutocomplete('team1Input', 'team1Results', (slug, name) => {{
            selectedTeam1 = {{ slug, name }};
            updateCompareButton();
        }});

        setupAutocomplete('team2Input', 'team2Results', (slug, name) => {{
            selectedTeam2 = {{ slug, name }};
            updateCompareButton();
        }});

        // Update compare button state
        function updateCompareButton() {{
            const button = document.getElementById('compareButton');
            if (selectedTeam1 && selectedTeam2) {{
                button.disabled = false;
                button.textContent = `Compare ${{selectedTeam1.name}} vs ${{selectedTeam2.name}}`;
            }} else {{
                button.disabled = true;
                button.textContent = 'Select Two Teams to Compare';
            }}
        }}

        // Compare button click handler
        document.getElementById('compareButton').addEventListener('click', function() {{
            if (selectedTeam1 && selectedTeam2) {{
                // Update URL
                const url = new URL(window.location);
                url.searchParams.set('team1', selectedTeam1.slug);
                url.searchParams.set('team2', selectedTeam2.slug);
                window.history.pushState({{}}, '', url);

                // Load comparison
                loadComparison(selectedTeam1.slug, selectedTeam2.slug);
            }}
        }});

        // Load comparison data
        async function loadComparison(team1Slug, team2Slug) {{
            try {{
                const emptyState = document.getElementById('emptyState');
                const comparisonResult = document.getElementById('comparisonResult');

                // Show loading state
                emptyState.style.display = 'none';
                comparisonResult.innerHTML = '<div style="text-align: center; padding: 40px;"><p>Loading comparison...</p></div>';
                comparisonResult.classList.add('show');

                // Fetch team data
                const [team1Response, team2Response] = await Promise.all([
                    fetch(`/data/${{team1Slug}}.json`),
                    fetch(`/data/${{team2Slug}}.json`)
                ]);

                if (!team1Response.ok || !team2Response.ok) {{
                    throw new Error('Failed to load team data');
                }}

                const team1Data = await team1Response.json();
                const team2Data = await team2Response.json();

                // Render comparison
                comparisonResult.innerHTML = renderComparison(team1Data, team2Data);
            }} catch (error) {{
                console.error('Error loading comparison:', error);
                const comparisonResult = document.getElementById('comparisonResult');
                comparisonResult.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #d32f2f;">
                        <h3>Error Loading Comparison</h3>
                        <p>Could not load data for one or both teams. Make sure both teams have been scraped.</p>
                    </div>
                `;
            }}
        }}

        function renderComparison(team1, team2) {{
            // Get team names from selected teams
            const team1Name = selectedTeam1.name;
            const team2Name = selectedTeam2.name;

            // Build best wins lists
            const team1WinsHTML = team1.best_wins.map(win => `
                <div class="win-item">
                    <strong>${{win.opponent}}</strong> (#${{win.net_rank}} NET) - ${{win.location}} - ${{win.quad}}
                </div>
            `).join('') || '<p style="color: #999;">No top wins recorded</p>';

            const team2WinsHTML = team2.best_wins.map(win => `
                <div class="win-item">
                    <strong>${{win.opponent}}</strong> (#${{win.net_rank}} NET) - ${{win.location}} - ${{win.quad}}
                </div>
            `).join('') || '<p style="color: #999;">No top wins recorded</p>';

            // Build losses lists
            const team1LossesHTML = team1.losses.map(loss => `
                <div class="win-item" style="border-left-color: #d32f2f;">
                    <strong>${{loss.opponent}}</strong> (#${{loss.net_rank}} NET) - ${{loss.location}} - ${{loss.quad}}
                </div>
            `).join('') || '<p style="color: #999;">No losses</p>';

            const team2LossesHTML = team2.losses.map(loss => `
                <div class="win-item" style="border-left-color: #d32f2f;">
                    <strong>${{loss.opponent}}</strong> (#${{loss.net_rank}} NET) - ${{loss.location}} - ${{loss.quad}}
                </div>
            `).join('') || '<p style="color: #999;">No losses</p>';

            return `
                <div class="comparison-grid">
                    <div class="team-card">
                        <h2>${{team1Name}}</h2>
                        <div class="stat-row">
                            <span class="stat-label">NET Rank</span>
                            <span class="stat-value">#${{team1.net_rank}}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">AP Rank</span>
                            <span class="stat-value">${{team1.ap_rank !== 'NR' ? '#' + team1.ap_rank : 'NR'}}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Record</span>
                            <span class="stat-value">${{team1.record}}</span>
                        </div>
                    </div>

                    <div class="team-card">
                        <h2>${{team2Name}}</h2>
                        <div class="stat-row">
                            <span class="stat-label">NET Rank</span>
                            <span class="stat-value">#${{team2.net_rank}}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">AP Rank</span>
                            <span class="stat-value">${{team2.ap_rank !== 'NR' ? '#' + team2.ap_rank : 'NR'}}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Record</span>
                            <span class="stat-value">${{team2.record}}</span>
                        </div>
                    </div>
                </div>

                <div class="quad-comparison">
                    <h3>Quadrant Record Comparison</h3>
                    <table class="quad-table">
                        <thead>
                            <tr>
                                <th>Quadrant</th>
                                <th>${{team1Name}}</th>
                                <th>${{team2Name}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Q1</strong></td>
                                <td>${{team1.quad_records.Q1.W}}-${{team1.quad_records.Q1.L}}</td>
                                <td>${{team2.quad_records.Q1.W}}-${{team2.quad_records.Q1.L}}</td>
                            </tr>
                            <tr>
                                <td><strong>Q2</strong></td>
                                <td>${{team1.quad_records.Q2.W}}-${{team1.quad_records.Q2.L}}</td>
                                <td>${{team2.quad_records.Q2.W}}-${{team2.quad_records.Q2.L}}</td>
                            </tr>
                            <tr>
                                <td><strong>Q3</strong></td>
                                <td>${{team1.quad_records.Q3.W}}-${{team1.quad_records.Q3.L}}</td>
                                <td>${{team2.quad_records.Q3.W}}-${{team2.quad_records.Q3.L}}</td>
                            </tr>
                            <tr>
                                <td><strong>Q4</strong></td>
                                <td>${{team1.quad_records.Q4.W}}-${{team1.quad_records.Q4.L}}</td>
                                <td>${{team2.quad_records.Q4.W}}-${{team2.quad_records.Q4.L}}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="comparison-grid">
                    <div class="wins-list">
                        <h4>${{team1Name}} - Best Wins</h4>
                        ${{team1WinsHTML}}
                    </div>

                    <div class="wins-list">
                        <h4>${{team2Name}} - Best Wins</h4>
                        ${{team2WinsHTML}}
                    </div>
                </div>

                <div class="comparison-grid">
                    <div class="wins-list">
                        <h4>${{team1Name}} - Losses</h4>
                        ${{team1LossesHTML}}
                    </div>

                    <div class="wins-list">
                        <h4>${{team2Name}} - Losses</h4>
                        ${{team2LossesHTML}}
                    </div>
                </div>
            `;
        }}

        // Check for URL parameters on load
        window.addEventListener('DOMContentLoaded', function() {{
            const urlParams = new URLSearchParams(window.location.search);
            const team1Param = urlParams.get('team1');
            const team2Param = urlParams.get('team2');

            if (team1Param && team2Param) {{
                // Find teams and populate
                const team1 = teams.find(t => t.slug === team1Param);
                const team2 = teams.find(t => t.slug === team2Param);

                if (team1 && team2) {{
                    document.getElementById('team1Input').value = team1.name;
                    document.getElementById('team2Input').value = team2.name;
                    selectedTeam1 = team1;
                    selectedTeam2 = team2;
                    updateCompareButton();
                    loadComparison(team1.slug, team2.slug);
                }}
            }}
        }});
    </script>
</body>
</html>'''

    # Write to output file
    output_path = Path(output_dir) / 'compare'
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / 'index.html'

    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"✅ Comparison tool generated: {output_file}")
    return True


if __name__ == "__main__":
    generate_comparison_page()
