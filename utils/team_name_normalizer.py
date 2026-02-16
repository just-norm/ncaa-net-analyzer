#!/usr/bin/env python3
"""
Comprehensive team name normalization and mapping
Handles differences between Sports-Reference and NCAA.com naming
"""

# Comprehensive mapping: Sports-Reference name -> NCAA.com name
TEAM_NAME_MAP = {
    # Common abbreviations
    'McNeese State': 'McNeese',
    'Army': 'Army West Point',
    'Western Carolina': 'Western Caro.',
    'Northern Arizona': 'Northern Ariz.',
    'Brigham Young': 'BYU',
    'BYU': 'BYU',
    'Connecticut': 'UConn',
    'connecticut': 'UConn',  # lowercase slug
    'Southern Methodist': 'SMU',

    # State vs St.
    'Michigan State': 'Michigan St.',
    'Ohio State': 'Ohio St.',
    'Penn State': 'Penn St.',
    'Iowa State': 'Iowa St.',
    'Kansas State': 'Kansas St.',
    'Oklahoma State': 'Oklahoma St.',
    'Oregon State': 'Oregon St.',
    'Washington State': 'Washington St.',
    'Arizona State': 'Arizona St.',
    'Colorado State': 'Colorado St.',
    'Boise State': 'Boise St.',
    'Fresno State': 'Fresno St.',
    'Utah State': 'Utah St.',
    'San Diego State': 'San Diego St.',
    'New Mexico State': 'New Mexico St.',
    'San Jose State': 'San Jose St.',
    'Florida State': 'Florida St.',
    'NC State': 'North Carolina St.',
    'Mississippi State': 'Mississippi St.',
    'South Dakota State': 'South Dakota St.',
    'Norfolk State': 'Norfolk St.',
    'Indiana State': 'Indiana St.',
    'Jackson State': 'Jackson St.',
    'Kent State': 'Kent St.',
    'Tennessee State': 'Tennessee St.',
    'South Carolina State': 'South Carolina St.',

    # Common variations
    'USC': 'Southern California',
    'Southern California': 'USC',
    'Southern': 'Southern U.',
    'UConn': 'Connecticut',
    'UNLV': 'UNLV',
    'UCF': 'Central Florida',
    'SMU': 'SMU',
    'TCU': 'TCU',
    'LSU': 'LSU',
    'UCLA': 'UCLA',
    'VCU': 'VCU',
    'Mississippi': 'Ole Miss',
    'Louisiana State': 'LSU',
    'Florida Gulf Coast': 'FGCU',
    'Long Island University': 'LIU',
    'Massachusetts-Lowell': 'UMass Lowell',
    'Texas-Rio Grande Valley': 'UTRGV',
    'East Tennessee State': 'ETSU',
    'South Carolina Upstate': 'USC Upstate',

    # Middle/Directional schools
    'Middle Tennessee': 'Middle Tenn.',
    'Middle Tennessee State': 'Middle Tenn.',
    'Western Kentucky': 'Western Ky.',
    'Eastern Kentucky': 'Eastern Ky.',
    'Northern Kentucky': 'Northern Ky.',
    'Eastern Illinois': 'Eastern Ill.',
    'Southern Illinois': 'Southern Ill.',
    'North Carolina Central': 'N.C. Central',
    'Central Arkansas': 'Central Ark.',

    # University variations
    'Miami (FL)': 'Miami (Fla.)',
    'Miami (OH)': 'Miami (Ohio)',
    'Miami': 'Miami (Fla.)',  # Usually refers to Florida

    # Other common mismatches
    'Saint Joseph\'s': 'St. Joseph\'s',
    'Saint Mary\'s': 'St. Mary\'s',
    'Saint Louis': 'Saint Louis',
    'La Salle': 'La Salle',
}


def normalize_team_name(name):
    """
    Normalize team name for matching
    Removes common words, standardizes formatting

    Args:
        name: Team name string

    Returns:
        str: Normalized name
    """
    if not name:
        return ""

    # Check exact mapping first
    if name in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[name]

    # Normalize for comparison
    normalized = name.lower().strip()

    # Remove common suffixes
    suffixes_to_remove = [
        'university',
        'college',
        'the',
        'of',
    ]

    for suffix in suffixes_to_remove:
        normalized = normalized.replace(f' {suffix} ', ' ')
        normalized = normalized.replace(f' {suffix}', '')
        normalized = normalized.replace(f'{suffix} ', '')

    # Standardize punctuation
    normalized = normalized.replace('.', '')
    normalized = normalized.replace('-', ' ')
    normalized = normalized.replace('\'', '')

    # Remove extra whitespace
    normalized = ' '.join(normalized.split())

    return normalized


def find_team_match(search_name, available_teams):
    """
    Find best match for team name in a list of available teams

    Args:
        search_name: Team name to search for
        available_teams: List or dict of available team names

    Returns:
        str or None: Matched team name or None if not found
    """
    # Handle dict vs list
    if isinstance(available_teams, dict):
        team_list = list(available_teams.keys())
    else:
        team_list = available_teams

    # Try exact match first
    if search_name in team_list:
        return search_name

    # Try mapping
    if search_name in TEAM_NAME_MAP:
        mapped_name = TEAM_NAME_MAP[search_name]
        if mapped_name in team_list:
            return mapped_name

    # Try case-insensitive
    search_lower = search_name.lower()
    for team in team_list:
        if team.lower() == search_lower:
            return team

    # Try normalized matching
    search_normalized = normalize_team_name(search_name)

    best_match = None
    best_score = 0

    for team in team_list:
        team_normalized = normalize_team_name(team)

        # Exact normalized match
        if search_normalized == team_normalized:
            return team

        # Word subset matching (all words from search in team)
        search_words = set(search_normalized.split())
        team_words = set(team_normalized.split())

        if search_words and team_words:
            # Calculate overlap
            common_words = search_words & team_words
            if common_words:
                score = len(common_words) / max(len(search_words), len(team_words))

                # Require high confidence
                if score > best_score and score >= 0.7:
                    best_score = score
                    best_match = team

    return best_match


def add_team_mapping(sports_ref_name, ncaa_name):
    """
    Add a new team name mapping

    Args:
        sports_ref_name: Name from Sports-Reference
        ncaa_name: Name from NCAA.com
    """
    TEAM_NAME_MAP[sports_ref_name] = ncaa_name
    print(f"Added mapping: '{sports_ref_name}' -> '{ncaa_name}'")


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ('McNeese State', 'McNeese'),
        ('Army', 'Army West Point'),
        ('Western Carolina', 'Western Carol.'),
        ('Brigham Young', 'BYU'),
        ('Michigan State', 'Michigan St.'),
    ]

    print("Testing team name mappings:")
    for sports_ref, expected_ncaa in test_cases:
        mapped = TEAM_NAME_MAP.get(sports_ref, 'NOT FOUND')
        status = '✅' if mapped == expected_ncaa else '❌'
        print(f"{status} {sports_ref} -> {mapped} (expected: {expected_ncaa})")
