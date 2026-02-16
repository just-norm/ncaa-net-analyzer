#!/usr/bin/env python3
"""
Updated batch scraper using combined Sports-Reference + NCAA.com scrapers
"""

import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.combined_scraper import scrape_team_complete, save_team_data
from utils.team_config import load_teams


def scrape_all_teams_v2(max_workers=2):
    """
    Scrape all teams using new combined scraper

    Args:
        max_workers: Number of parallel scrapers (default: 2 for respectful rate limiting)

    Returns:
        dict: Results summary
    """
    print("=" * 70)
    print("🏀 NCAA Batch Scraper V2 (Sports-Reference + NCAA.com)")
    print("=" * 70)
    print()

    # Load teams
    teams = load_teams()
    active_teams = [t for t in teams if t.get('active', True)]

    print(f"📋 Found {len(active_teams)} active teams\n")

    # Setup output directory
    output_base_dir = Path(__file__).parent.parent / 'data' / 'teams'

    # Track results
    results = {
        'successful': [],
        'failed': []
    }

    # Scrape teams
    print(f"🔄 Scraping teams (max {max_workers} parallel)...")
    print("-" * 70)

    def scrape_single(team):
        """Scrape a single team"""
        team_name = team['name']
        team_slug = team['slug']

        try:
            # Scrape complete data
            team_data = scrape_team_complete(team_name)

            if not team_data:
                return (team_name, False, "No data returned")

            # Save data
            output_dir = output_base_dir / team_slug
            success = save_team_data(team_data, output_dir)

            if success:
                return (team_name, True, None)
            else:
                return (team_name, False, "Failed to save data")

        except Exception as e:
            return (team_name, False, str(e))

    # Execute in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_team = {executor.submit(scrape_single, team): team for team in active_teams}

        for future in as_completed(future_to_team):
            team_name, success, error = future.result()

            if success:
                results['successful'].append(team_name)
                print(f"  ✅ {team_name}")
            else:
                results['failed'].append((team_name, error))
                print(f"  ❌ {team_name}: {error}")

            # Rate limiting
            time.sleep(1)

    print("-" * 70)
    print()

    # Summary
    print("=" * 70)
    print("📊 Scraping Summary")
    print("=" * 70)
    print(f"✅ Successful: {len(results['successful'])}/{len(active_teams)}")

    if results['failed']:
        print(f"❌ Failed: {len(results['failed'])}/{len(active_teams)}")
        print("\nFailed teams:")
        for team_name, error in results['failed']:
            print(f"  - {team_name}: {error}")
    else:
        print("🎉 All teams scraped successfully!")

    print("=" * 70)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Batch scrape NCAA team data (V2)')
    parser.add_argument('--workers', type=int, default=2,
                        help='Number of parallel workers (default: 2)')

    args = parser.parse_args()

    results = scrape_all_teams_v2(max_workers=args.workers)

    # Exit with error code if any failures
    sys.exit(0 if not results['failed'] else 1)
