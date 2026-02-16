#!/usr/bin/env python3
"""
Scrape AP Poll rankings (Top 25)
Saves to data/ap_poll/{date}.csv
"""

import csv
import sys
import re
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def scrape_ap_poll():
    """
    Scrape AP Poll rankings from NCAA.com

    Returns:
        dict: {'team_name': rank}
    """
    print("🔍 Scraping AP Poll from NCAA.com...")

    url = "https://www.ncaa.com/rankings/basketball-men/d1/associated-press"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all rank items
        rank_items = soup.find_all('div', class_='rankings-team') or soup.find_all('td', class_='team')

        rankings = {}

        for item in rank_items:
            rank_text = item.find('span', class_='rank-number') or item.find('div', class_='rank-number')
            team_text = item.find('span', class_='team-name') or item.find('a', class_='team-name')

            if rank_text and team_text:
                try:
                    rank = int(rank_text.get_text(strip=True).replace('.', ''))
                    team = team_text.get_text(strip=True)
                    rankings[team] = rank
                except ValueError:
                    continue
            else:
                # Alternative parsing: Look for rank in text
                text = item.get_text()
                rank_match = re.search(r'(\d+)\.?\s+(.+)', text)
                if rank_match:
                    try:
                        rank = int(rank_match.group(1))
                        team = rank_match.group(2).strip()
                        rankings[team] = rank
                    except ValueError:
                        continue

        print(f"✅ Scraped {len(rankings)} teams from AP Poll")
        return rankings

    except Exception as e:
        print(f"❌ Error scraping AP Poll: {e}")
        return {}


def save_ap_poll(rankings, output_dir='data/ap_poll'):
    """
    Save AP Poll rankings to CSV file with today's date

    Args:
        rankings: dict of team rankings
        output_dir: output directory

    Returns:
        Path to saved file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create filename with today's date
    today = datetime.now().strftime('%Y-%m-%d')
    csv_file = output_path / f'{today}.csv'

    print(f"💾 Saving AP Poll to {csv_file}...")

    # Write CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['rank', 'team'])

        # Sort by rank
        sorted_teams = sorted(rankings.items(), key=lambda x: x[1])

        for team_name, rank in sorted_teams:
            writer.writerow([rank, team_name])

    # Create/update 'latest.csv' symlink
    latest_link = output_path / 'latest.csv'
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()

    # Create relative symlink
    latest_link.symlink_to(csv_file.name)

    print(f"✅ Saved {len(rankings)} teams to {csv_file}")
    print(f"🔗 Updated latest.csv symlink")

    return csv_file


def main():
    """Main function"""
    print("=" * 60)
    print("🏀 AP Poll Scraper")
    print("=" * 60)
    print()

    # Scrape AP Poll
    rankings = scrape_ap_poll()

    if not rankings:
        print("⚠️  No AP Poll rankings found (might not be poll week)")
        # Don't exit with error - AP poll only updates weekly
        return 0

    # Save rankings
    csv_file = save_ap_poll(rankings)

    print()
    print("=" * 60)
    print("✅ AP Poll scraping completed!")
    print(f"📁 Output: {csv_file}")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
