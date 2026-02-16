"""
Team configuration loading utilities
"""
import json
from pathlib import Path


def get_config_path(filename):
    """Get absolute path to config file"""
    # Get the project root (parent of utils/)
    project_root = Path(__file__).parent.parent
    return project_root / 'config' / filename


def load_teams():
    """
    Load team registry from teams.json

    Returns:
        list: List of team dicts with name, slug, conference, active fields
    """
    config_file = get_config_path('teams.json')

    with open(config_file, 'r') as f:
        data = json.load(f)

    return data.get('teams', [])


def get_team_by_slug(slug):
    """
    Get team configuration by slug

    Args:
        slug: Team slug (e.g., 'michigan', 'duke')

    Returns:
        dict: Team configuration or None if not found
    """
    teams = load_teams()
    for team in teams:
        if team['slug'] == slug:
            return team
    return None


def get_team_colors(slug):
    """
    Get team branding colors by slug

    Args:
        slug: Team slug (e.g., 'michigan', 'duke')

    Returns:
        dict: Colors dict with 'primary', 'secondary', 'name_color' keys
              Returns default colors if team not found
    """
    config_file = get_config_path('team_colors.json')

    with open(config_file, 'r') as f:
        colors = json.load(f)

    # Return team colors or default
    return colors.get(slug, {
        'primary': '#003366',
        'secondary': '#FFFFFF',
        'name_color': '#FFFFFF'
    })


def load_all_team_colors():
    """
    Load all team colors

    Returns:
        dict: Dictionary mapping slugs to color dicts
    """
    config_file = get_config_path('team_colors.json')

    with open(config_file, 'r') as f:
        return json.load(f)
