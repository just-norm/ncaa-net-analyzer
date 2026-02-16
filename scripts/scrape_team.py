#!/usr/bin/env python3
"""
Command-line tool to scrape any team's data from bballnet.com
Usage: python scrape_team.py <team-slug>
Example: python scrape_team.py michigan
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from bballnet_scraper import scrape_team_data, save_team_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scrape_team.py <team-slug>")
        print("Example: python scrape_team.py michigan")
        sys.exit(1)

    team_slug = sys.argv[1].lower()

    # Scrape the data
    team_data = scrape_team_data(team_slug)

    if team_data:
        # Save to teams/<team_slug>/ folder
        save_team_data(team_data, team_slug)
    else:
        print(f"❌ Failed to scrape {team_slug}")
        sys.exit(1)
