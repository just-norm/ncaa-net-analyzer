#!/usr/bin/env python3
"""
Generate JSON data files for each team for use in comparison tool
"""

import csv
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_team_json(team_slug, output_dir='public/data'):
    """
    Generate JSON data file for a team

    Args:
        team_slug: Team slug
        output_dir: Output directory for JSON files

    Returns:
        dict: Team data or None if team data not found
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

    if not schedule_file.exists():
        return None

    quad_records = {
        'Q1': {'W': 0, 'L': 0},
        'Q2': {'W': 0, 'L': 0},
        'Q3': {'W': 0, 'L': 0},
        'Q4': {'W': 0, 'L': 0}
    }
    best_wins = []
    all_losses = []
    total_wins = 0
    total_losses = 0

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

                # Track best wins (Q1/Q2 wins)
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

                # Track all losses
                if net_rank_opp != 'NR':
                    try:
                        all_losses.append({
                            'opponent': opponent,
                            'net_rank': int(net_rank_opp),
                            'location': location,
                            'quad': quad
                        })
                    except ValueError:
                        pass

    # Sort best wins by opponent NET rank (lower is better)
    best_wins.sort(key=lambda x: x['net_rank'])
    # Sort all losses by opponent NET rank (lower rank = worse loss)
    all_losses.sort(key=lambda x: x['net_rank'])

    # Create team data object
    team_data = {
        'slug': team_slug,
        'net_rank': net_rank,
        'ap_rank': ap_rank,
        'record': f"{total_wins}-{total_losses}",
        'quad_records': quad_records,
        'best_wins': best_wins[:5],  # Top 5 wins
        'losses': all_losses  # All losses
    }

    # Write JSON file
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f'{team_slug}.json'

    with open(output_file, 'w') as f:
        json.dump(team_data, f, indent=2)

    return team_data


def generate_all_team_json(output_dir='public/data'):
    """
    Generate JSON files for all teams

    Args:
        output_dir: Output directory for JSON files
    """
    from utils.team_config import load_teams

    print("📊 Generating team JSON data files...")

    teams = load_teams()
    active_teams = [t for t in teams if t.get('active', True)]

    successful = 0
    failed = 0

    for team in active_teams:
        team_slug = team['slug']
        team_name = team['name']

        try:
            result = generate_team_json(team_slug, output_dir)
            if result:
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {team_name}: {e}")
            failed += 1

    print(f"✅ Generated {successful} JSON files")
    if failed > 0:
        print(f"⚠️  Skipped {failed} teams (no data)")

    return successful


if __name__ == "__main__":
    generate_all_team_json()
