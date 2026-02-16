#!/usr/bin/env python3
"""
Diagnostic tool to find team name mismatches between data sources
"""

import sys
import csv
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.ncaa_net_scraper import scrape_net_rankings
from utils.team_name_normalizer import find_team_match, add_team_mapping, TEAM_NAME_MAP


def find_mismatches_in_schedule(schedule_file):
    """
    Find opponents in schedule that don't have NET rankings

    Args:
        schedule_file: Path to schedule CSV file

    Returns:
        list: List of (opponent, reason) tuples
    """
    mismatches = []

    with open(schedule_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            opponent = row['opponent']
            net_rank = row.get('net_rank', '')

            # If NET rank is empty or NR, it might be a mismatch
            if not net_rank or net_rank == 'NR' or net_rank == '':
                # Skip TBD games
                if row['result'] == 'TBD':
                    continue
                mismatches.append(opponent)

    return list(set(mismatches))  # Unique opponents


def suggest_matches(mismatches, net_rankings):
    """
    Suggest potential matches from NET rankings

    Args:
        mismatches: List of unmatched team names
        net_rankings: Dict of NET rankings

    Returns:
        dict: Suggested matches
    """
    suggestions = {}

    for opponent in mismatches:
        match = find_team_match(opponent, net_rankings)
        if match:
            suggestions[opponent] = {
                'suggested_match': match,
                'net_rank': net_rankings[match]['rank'],
                'confidence': 'high' if match in TEAM_NAME_MAP.values() else 'medium'
            }
        else:
            # Try to find partial matches
            opponent_lower = opponent.lower()
            partials = []
            for team in net_rankings.keys():
                if opponent_lower in team.lower() or team.lower() in opponent_lower:
                    partials.append(team)

            if partials:
                suggestions[opponent] = {
                    'suggested_match': partials[0] if len(partials) == 1 else partials,
                    'net_rank': net_rankings[partials[0]]['rank'] if len(partials) == 1 else '?',
                    'confidence': 'low'
                }
            else:
                suggestions[opponent] = {
                    'suggested_match': None,
                    'net_rank': None,
                    'confidence': 'none'
                }

    return suggestions


def analyze_team(team_slug):
    """
    Analyze a single team's schedule for mismatches

    Args:
        team_slug: Team slug (e.g., 'michigan')
    """
    schedule_file = Path(__file__).parent.parent / 'data' / 'teams' / team_slug / f'{team_slug}_schedule_analysis.csv'

    if not schedule_file.exists():
        print(f"❌ Schedule file not found: {schedule_file}")
        return

    print(f"\n📊 Analyzing {team_slug}...")
    print("=" * 70)

    # Get NET rankings
    print("Fetching NET rankings...")
    net_rankings = scrape_net_rankings()

    # Find mismatches
    mismatches = find_mismatches_in_schedule(schedule_file)

    if not mismatches:
        print("✅ No mismatches found!")
        return

    print(f"\n⚠️  Found {len(mismatches)} opponents without NET rankings:\n")

    # Suggest matches
    suggestions = suggest_matches(mismatches, net_rankings)

    for opponent, suggestion in suggestions.items():
        match = suggestion['suggested_match']
        rank = suggestion['net_rank']
        conf = suggestion['confidence']

        if match and not isinstance(match, list):
            print(f"  '{opponent}' -> '{match}' (NET #{rank}) [{conf} confidence]")
        elif isinstance(match, list):
            print(f"  '{opponent}' -> Multiple matches: {', '.join(match[:3])} [{conf}]")
        else:
            print(f"  '{opponent}' -> NO MATCH FOUND ❌")

    # Generate mapping code
    print(f"\n📝 Suggested code to add to team_name_normalizer.py:")
    print("-" * 70)
    for opponent, suggestion in suggestions.items():
        match = suggestion['suggested_match']
        if match and not isinstance(match, list) and suggestion['confidence'] in ['high', 'medium']:
            print(f"    '{opponent}': '{match}',")


def analyze_all_teams():
    """Analyze all teams for mismatches"""
    teams_dir = Path(__file__).parent.parent / 'data' / 'teams'

    if not teams_dir.exists():
        print("❌ Teams directory not found")
        return

    team_dirs = [d for d in teams_dir.iterdir() if d.is_dir()]

    for team_dir in sorted(team_dirs):
        analyze_team(team_dir.name)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Analyze specific team
        team_slug = sys.argv[1]
        analyze_team(team_slug)
    else:
        # Analyze all teams
        print("🔍 Analyzing all teams for name mismatches...")
        analyze_all_teams()
