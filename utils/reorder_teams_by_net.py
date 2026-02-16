#!/usr/bin/env python3
"""
One-time script to reorder teams.json by NET ranking priority
"""

import json
from pathlib import Path

# Top 30 teams by NET ranking (as of current data)
TOP_30_NET = [
    "Michigan", "Duke", "Arizona", "Houston", "Purdue",
    "Gonzaga", "Illinois", "Iowa St.", "Florida", "UConn",
    "Nebraska", "Louisville", "Vanderbilt", "Kansas", "Michigan St.",
    "Texas Tech", "Saint Louis", "Arkansas", "Virginia", "BYU",
    "Alabama", "Tennessee", "Utah St.", "St. John's", "North Carolina",
    "Saint Mary's", "Iowa", "Kentucky", "NC State", "Villanova"
]

def reorder_teams():
    """Reorder teams.json to prioritize top 30 NET teams"""

    # Load current teams.json
    teams_file = Path(__file__).parent.parent / 'config' / 'teams.json'
    with open(teams_file, 'r') as f:
        data = json.load(f)

    teams = data['teams']

    # Create lookup by name
    teams_by_name = {team['name']: team for team in teams}

    # Build new ordered list
    ordered_teams = []

    # Add top 30 teams first (in NET order)
    for team_name in TOP_30_NET:
        if team_name in teams_by_name:
            ordered_teams.append(teams_by_name[team_name])
        else:
            print(f"⚠️  Warning: Top 30 team '{team_name}' not found in teams.json")

    # Add remaining teams alphabetically
    remaining_teams = [t for t in teams if t['name'] not in TOP_30_NET]
    remaining_teams.sort(key=lambda t: t['name'])
    ordered_teams.extend(remaining_teams)

    # Verify count
    assert len(ordered_teams) == len(teams), "Team count mismatch!"

    # Save reordered teams
    data['teams'] = ordered_teams

    with open(teams_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Reordered {len(teams)} teams")
    print(f"📊 Top 30 NET teams are now first")
    print(f"🔤 Remaining {len(remaining_teams)} teams alphabetically ordered")
    print("\nFirst 10 teams in new order:")
    for i, team in enumerate(ordered_teams[:10], 1):
        print(f"  {i}. {team['name']}")

if __name__ == "__main__":
    reorder_teams()
