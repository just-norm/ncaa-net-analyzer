#!/usr/bin/env python3
"""
Scraper for NCAA.com official NET rankings
"""

import requests
from bs4 import BeautifulSoup
import re


def scrape_net_rankings():
    """
    Scrape complete NET rankings from NCAA.com

    Returns:
        dict: {team_name: {'rank': int, 'record': str, 'conference': str}}
    """
    url = "https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings"

    print(f"📊 Scraping NET rankings from NCAA.com...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        rankings = {}

        # Find the rankings table
        table = soup.find('table')

        if not table:
            print("❌ Could not find NET rankings table")
            return {}

        rows = table.find_all('tr')[1:]  # Skip header

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                try:
                    # Rank
                    rank_text = cols[0].get_text(strip=True)
                    rank_match = re.search(r'(\d+)', rank_text)
                    if not rank_match:
                        continue
                    rank = int(rank_match.group(1))

                    # Team name
                    team_cell = cols[1]
                    team_link = team_cell.find('a')
                    if team_link:
                        team_name = team_link.get_text(strip=True)
                    else:
                        team_name = team_cell.get_text(strip=True)

                    # Record (if available)
                    record = ''
                    if len(cols) >= 3:
                        record_text = cols[2].get_text(strip=True)
                        record_match = re.search(r'(\d+-\d+)', record_text)
                        if record_match:
                            record = record_match.group(1)

                    # Conference (if available)
                    conference = ''
                    if len(cols) >= 4:
                        conference = cols[3].get_text(strip=True)

                    rankings[team_name] = {
                        'rank': rank,
                        'record': record,
                        'conference': conference
                    }

                except (ValueError, IndexError, AttributeError):
                    continue

        print(f"✅ Scraped {len(rankings)} teams from NET rankings")
        return rankings

    except Exception as e:
        print(f"❌ Error scraping NET rankings: {e}")
        return {}


def get_team_net_rank(team_name, rankings=None):
    """
    Get NET rank for a specific team

    Args:
        team_name: Team name
        rankings: Pre-fetched rankings dict (optional)

    Returns:
        int: NET rank or None
    """
    if rankings is None:
        rankings = scrape_net_rankings()

    # Try exact match first
    if team_name in rankings:
        return rankings[team_name]['rank']

    # Try case-insensitive match
    for team, data in rankings.items():
        if team.lower() == team_name.lower():
            return data['rank']

    return None


if __name__ == "__main__":
    # Test scraping
    rankings = scrape_net_rankings()

    if rankings:
        print(f"\nTop 10 NET Rankings:")
        sorted_teams = sorted(rankings.items(), key=lambda x: x[1]['rank'])
        for team, data in sorted_teams[:10]:
            print(f"  #{data['rank']}: {team} ({data['record']})")
