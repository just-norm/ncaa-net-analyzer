"""
Quadrant calculation logic for NCAA NET rankings
"""


def calculate_quadrant(net_rank, location):
    """
    Determine quadrant (Q1-Q4) based on opponent's NET rank and game location

    Quadrant definitions:
    - Q1: Home 1-30, Neutral 1-50, Away 1-75
    - Q2: Home 31-75, Neutral 51-100, Away 76-135
    - Q3: Home 76-160, Neutral 101-200, Away 136-240
    - Q4: All other games

    Args:
        net_rank: Opponent's NET ranking (int or str that can be converted to int)
        location: Game location ('Home', 'Away', or 'Neutral')

    Returns:
        str: Quadrant classification ('Q1', 'Q2', 'Q3', or 'Q4')
    """
    # Handle non-numeric ranks
    try:
        rank = int(net_rank)
    except (ValueError, TypeError):
        return 'Q4'

    location = location.strip()

    # Q1 thresholds
    if location == 'Home' and rank <= 30:
        return 'Q1'
    elif location == 'Neutral' and rank <= 50:
        return 'Q1'
    elif location == 'Away' and rank <= 75:
        return 'Q1'

    # Q2 thresholds
    elif location == 'Home' and rank <= 75:
        return 'Q2'
    elif location == 'Neutral' and rank <= 100:
        return 'Q2'
    elif location == 'Away' and rank <= 135:
        return 'Q2'

    # Q3 thresholds
    elif location == 'Home' and rank <= 160:
        return 'Q3'
    elif location == 'Neutral' and rank <= 200:
        return 'Q3'
    elif location == 'Away' and rank <= 240:
        return 'Q3'

    # Q4: Everything else
    else:
        return 'Q4'
