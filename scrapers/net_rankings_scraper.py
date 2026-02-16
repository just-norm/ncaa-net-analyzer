#!/usr/bin/env python3
"""
Scrape complete NET rankings for all NCAA Division I teams
Saves to data/net_rankings/{date}.csv
"""

import csv
import sys
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def scrape_net_rankings():
    """
    Scrape complete NET rankings from NCAA.com

    Returns:
        dict: {'team_name': {'rank': int, 'record': str, 'conference': str}}
    """
    print("🔍 Scraping NET rankings from NCAA.com...")

    url = "https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the rankings table
        table = soup.find('table', class_='rankings-table') or soup.find('table')

        if not table:
            print("❌ Could not find NET rankings table")
            return None

        rankings = {}
        rows = table.find_all('tr')[1:]  # Skip header

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                try:
                    rank = cols[0].get_text(strip=True)
                    team = cols[1].get_text(strip=True)

                    # Extract conference and record if available
                    conference = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                    record = cols[3].get_text(strip=True) if len(cols) > 3 else ''

                    rankings[team] = {
                        'rank': int(rank),
                        'record': record,
                        'conference': conference
                    }
                except (ValueError, IndexError):
                    continue

        print(f"✅ Scraped {len(rankings)} teams from NET rankings")
        return rankings

    except Exception as e:
        print(f"❌ Error scraping NET rankings: {e}")
        return None


def save_net_rankings(rankings, output_dir='data/net_rankings'):
    """
    Save NET rankings to CSV file with today's date

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

    print(f"💾 Saving NET rankings to {csv_file}...")

    # Write CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['rank', 'team', 'conference', 'record'])

        # Sort by rank
        sorted_teams = sorted(rankings.items(), key=lambda x: x[1]['rank'])

        for team_name, data in sorted_teams:
            writer.writerow([
                data['rank'],
                team_name,
                data['conference'],
                data['record']
            ])

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
    print("🏀 NCAA NET Rankings Scraper")
    print("=" * 60)
    print()

    # Scrape rankings
    rankings = scrape_net_rankings()

    if not rankings:
        print("❌ Failed to scrape NET rankings")
        sys.exit(1)

    # Save rankings
    csv_file = save_net_rankings(rankings)

    print()
    print("=" * 60)
    print("✅ NET Rankings scraping completed!")
    print(f"📁 Output: {csv_file}")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
