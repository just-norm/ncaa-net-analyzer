"""
Fuzzy team name matching utilities
Handles variations like "USC" vs "Southern California", "Penn State" vs "Penn St."
"""


def normalize_team_name(name):
    """
    Normalize team names for matching

    Args:
        name: Team name string

    Returns:
        str: Normalized lowercase team name
    """
    name = name.lower().strip()

    # Handle common variations
    replacements = {
        'st.': 'st',
        'state': 'st',
        'university': '',
        'the': '',
        '-': ' ',
        '.': ''
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    # Remove extra whitespace
    name = ' '.join(name.split())

    return name


def find_team_in_rankings(team_name, rankings_dict):
    """
    Find team in rankings dictionary using fuzzy matching

    Args:
        team_name: Team name to search for
        rankings_dict: Dict mapping team names to rankings data

    Returns:
        Ranking data for team or None if not found
    """
    # Common team name variations mapping
    team_name_map = {
        'USC': 'Southern California',
        'Middle Tennessee': 'Middle Tenn.',
        'Middle Tenn.': 'Middle Tenn.',
        'Penn State': 'Penn St.',
        'Michigan State': 'Michigan St.',
        'Ohio State': 'Ohio St.',
        'San Diego State': 'San Diego St.',
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
    }

    # Check mapping first
    if team_name in team_name_map:
        team_name = team_name_map[team_name]

    # Try exact match
    if team_name in rankings_dict:
        return rankings_dict[team_name]

    # Common variations
    variations = [
        team_name,
        team_name.replace('State', 'St.'),
        team_name.replace('St.', 'State'),
        team_name.replace(' St', ' State'),
    ]

    for variation in variations:
        if variation in rankings_dict:
            return rankings_dict[variation]

    # Try normalized matching
    normalized_search = normalize_team_name(team_name)

    best_match = None
    best_match_data = None

    for net_team, data in rankings_dict.items():
        normalized_net = normalize_team_name(net_team)

        # Exact match after normalization
        if normalized_search == normalized_net:
            return data

        # Only match if search term is a complete word in the NET team name
        # This prevents "Michigan" from matching "Michigan State"
        words_search = set(normalized_search.split())
        words_net = set(normalized_net.split())

        # If all words from search are in NET team, and lengths are similar
        if words_search.issubset(words_net) and len(words_search) >= len(words_net) - 1:
            if best_match is None or len(normalized_net) < len(best_match):
                best_match = normalized_net
                best_match_data = data

    return best_match_data
