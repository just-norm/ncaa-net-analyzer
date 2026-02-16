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

        # Find the rankings table
        table = soup.find('table')

        if not table:
            print("❌ Could not find AP Poll table")
            return {}

        rankings = {}
        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                try:
                    # First column is rank
                    rank_text = cols[0].get_text(strip=True)
                    rank = int(rank_text)

                    # Second column is school name (may include votes in parentheses)
                    school_text = cols[1].get_text(strip=True)
                    # Remove vote count in parentheses if present
                    team = re.sub(r'\s*\(\d+\)\s*$', '', school_text).strip()

                    rankings[team] = rank
                except (ValueError, IndexError):
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
