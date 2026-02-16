#!/usr/bin/env python3
"""
Populate sports_reference_slug field in teams.json using existing mappings
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.team_name_normalizer import TEAM_NAME_MAP


def generate_sports_ref_slug(team_name):
    """
    Generate Sports-Reference URL slug from team name
    Uses normalizer to convert "St." to "State" first

    Args:
        team_name: Display name of the team

    Returns:
        str: Sports-Reference URL slug
    """

    # Special cases that don't follow patterns
    special_cases = {
        'McNeese': 'mcneese-state',
        'South Fla.': 'south-florida',
        'Saint Mary\'s (CA)': 'saint-marys-ca',
        'St. John\'s (NY)': 'st-johns-ny',
        'A&M-Corpus Christi': 'texas-am-corpus-christi',
        'Miami (FL)': 'miami-fl',
        'Miami (OH)': 'miami-ohio',
        'Illinois St.': 'illinois-state',
        'Wichita St.': 'wichita-state',
    }

    # Check special cases first
    if team_name in special_cases:
        return special_cases[team_name]

    # Handle abbreviations - teams that are commonly known by initials
    abbreviation_map = {
        'TCU': 'texas-christian',
        'VCU': 'virginia-commonwealth',
        'UCF': 'central-florida',
        'LSU': 'louisiana-state',
        'SFA': 'stephen-f-austin',
        'UNI': 'northern-iowa',
        'BYU': 'brigham-young',
        'SMU': 'southern-methodist',
        'UConn': 'connecticut',
        'USC': 'southern-california',
        'UCLA': 'ucla',
        'UNLV': 'nevada-las-vegas',
        'UTEP': 'texas-el-paso',
        'UAB': 'alabama-birmingham',
        'UIC': 'illinois-chicago',
        'UMBC': 'maryland-baltimore-county',
        'UNCG': 'north-carolina-greensboro',
        'IUPUI': 'iupui',
        'LIU': 'long-island-university',
        'LMU': 'loyola-marymount',
        'FIU': 'florida-international',
        'FDU': 'fairleigh-dickinson',
        'NJIT': 'njit',
        'MIT': 'mit',
        'RIT': 'rit',
    }

    # Check abbreviations
    if team_name in abbreviation_map:
        return abbreviation_map[team_name]

    # If team has "St." convert to "State" using normalizer
    if 'St.' in team_name and team_name in TEAM_NAME_MAP:
        full_name = TEAM_NAME_MAP[team_name]
        # Convert to slug: "San Diego State" → "san-diego-state"
        return full_name.lower().replace(' ', '-').replace('&', '').replace("'", '')

    # Handle generic parenthetical disambiguation
    # e.g., "Alabama (FL)" → "alabama-fl"
    if '(OH)' in team_name:
        return team_name.replace('(OH)', '').strip().lower().replace(' ', '-').replace('&', '').replace("'", '')
    if '(FL)' in team_name:
        return team_name.replace('(FL)', '').strip().lower().replace(' ', '-').replace('&', '').replace("'", '')
    if '(CA)' in team_name:
        return team_name.replace('(CA)', '').strip().lower().replace(' ', '-').replace('&', '').replace("'", '')
    if '(NY)' in team_name:
        return team_name.replace('(NY)', '').strip().lower().replace(' ', '-').replace('&', '').replace("'", '')

    # Default: lowercase with hyphens, remove special characters
    return team_name.lower().replace(' ', '-').replace('&', '').replace("'", '').replace('(', '').replace(')', '').replace('.', '')


def populate_sports_ref_slugs():
    """Add sports_reference_slug to all teams in teams.json"""
    config_path = Path(__file__).parent.parent / 'config' / 'teams.json'

    if not config_path.exists():
        print(f"❌ Error: {config_path} not found")
        return False

    print(f"📂 Loading teams from {config_path}")

    with open(config_path, 'r') as f:
        data = json.load(f)

    print(f"⚙️  Processing {len(data['teams'])} teams...")

    # Track statistics
    added = 0
    updated = 0

    for team in data['teams']:
        team_name = team['name']
        new_slug = generate_sports_ref_slug(team_name)

        if 'sports_reference_slug' in team:
            if team['sports_reference_slug'] != new_slug:
                print(f"  ⚠️  Updating {team_name}: {team['sports_reference_slug']} → {new_slug}")
                team['sports_reference_slug'] = new_slug
                updated += 1
        else:
            team['sports_reference_slug'] = new_slug
            added += 1

    # Write back to file with pretty formatting
    with open(config_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Successfully updated {config_path}")
    print(f"   Added sports_reference_slug to {added} teams")
    if updated > 0:
        print(f"   Updated {updated} existing slugs")
    print(f"   Total teams: {len(data['teams'])}")

    return True


if __name__ == '__main__':
    success = populate_sports_ref_slugs()
    sys.exit(0 if success else 1)
