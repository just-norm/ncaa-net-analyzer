#!/usr/bin/env python3
"""
Scraper for Sports-Reference.com team schedules
Clean table structure with home/away/neutral indicators
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


def scrape_team_schedule(team_name, year=2026):
    """
    Scrape team schedule from Sports-Reference

    Args:
        team_name: Team name (will be converted to slug)
        year: Season year (default: 2026)

    Returns:
        list: Schedule with games
    """
    # Manual mappings for teams with non-standard Sports-Reference URLs
    url_mappings = {
        'Iowa St.': 'iowa-state',
        'Michigan St.': 'michigan-state',
        'Utah St.': 'utah-state',
        'NC State': 'north-carolina-state',
        'BYU': 'brigham-young',
        'UConn': 'connecticut',
        'A&M-Corpus Christi': 'texas-am-corpus-christi',
        'Saint Mary\'s': 'saint-marys-ca',
        'St. John\'s': 'st-johns-ny',
    }

    # Check if team has manual mapping
    if team_name in url_mappings:
        team_slug = url_mappings[team_name]
    else:
        # Default: convert to lowercase with hyphens
        team_slug = team_name.lower().replace(' ', '-').replace('&', '')

    url = f'https://www.sports-reference.com/cbb/schools/{team_slug}/men/{year}-schedule.html'

    print(f"📥 Scraping {team_name} schedule from Sports-Reference...")
    print(f"   URL: {url}")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the schedule table
        schedule_table = soup.find('table', {'id': 'schedule'})

        if not schedule_table:
            print(f"❌ Could not find schedule table for {team_name}")
            return []

        schedule = []
        rows = schedule_table.find('tbody').find_all('tr')

        for row in rows:
            # Skip header rows
            if row.get('class') and 'thead' in row.get('class'):
                continue

            cells = row.find_all(['td', 'th'])
            if len(cells) < 6:
                continue

            try:
                # Date (Cell 1)
                date_cell = cells[1]
                date_text = date_cell.get_text(strip=True)

                # Parse date (format: "Mon, Nov 4, 2025")
                date_match = re.search(r'(\w+)\s+(\d+),\s+(\d{4})', date_text)
                if date_match:
                    month = date_match.group(1)
                    day = date_match.group(2)
                    date = f"{month} {day}"
                else:
                    date = date_text

                # Location (Cell 4: @ = away, N = neutral, empty = home)
                location_cell = cells[4]
                location_text = location_cell.get_text(strip=True)

                if location_text == '@':
                    location = 'Away'
                elif location_text == 'N':
                    location = 'Neutral'
                else:
                    location = 'Home'

                # Opponent (Cell 5)
                opponent_cell = cells[5]
                opponent_link = opponent_cell.find('a')
                if opponent_link:
                    opponent = opponent_link.get_text(strip=True)
                else:
                    opponent = opponent_cell.get_text(strip=True)

                # Remove rankings from opponent name (e.g., "(1) Duke" -> "Duke")
                opponent = re.sub(r'^\(\d+\)\s*', '', opponent)

                # Result (Cell 8: W/L or empty for future games)
                if len(cells) > 8:
                    result_cell = cells[8]
                    result_text = result_cell.get_text(strip=True)

                    if result_text.upper() == 'W':
                        result = 'W'
                    elif result_text.upper() == 'L':
                        result = 'L'
                    else:
                        result = 'TBD'
                else:
                    result = 'TBD'

                # Score (Cells 9 and 10: team points, opponent points)
                score = ''
                if len(cells) > 10 and result in ['W', 'L']:
                    pts = cells[9].get_text(strip=True)
                    opp_pts = cells[10].get_text(strip=True)

                    if pts and opp_pts:
                        if result == 'W':
                            score = f"{pts}-{opp_pts}"
                        else:
                            score = f"{opp_pts}-{pts}"

                schedule.append({
                    'date': date,
                    'opponent': opponent,
                    'location': location,
                    'result': result,
                    'score': score
                })

            except (IndexError, AttributeError) as e:
                continue

        print(f"✅ Scraped {len(schedule)} games for {team_name}")
        return schedule

    except Exception as e:
        print(f"❌ Error scraping {team_name}: {e}")
        return []


if __name__ == "__main__":
    # Test with Michigan
    schedule = scrape_team_schedule('Michigan')
    if schedule:
        print(f"\nFirst 5 games:")
        for game in schedule[:5]:
            print(f"  {game['date']}: {game['result']} vs {game['opponent']} ({game['location']}) {game['score']}")
