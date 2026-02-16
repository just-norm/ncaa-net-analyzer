#!/usr/bin/env python3
"""
Batch scraper to fetch data for multiple teams
"""

import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.bballnet_scraper import scrape_team_data, save_team_data, scrape_ap_rankings
from utils.team_config import load_teams


def scrape_single_team(team, ap_rankings, output_base_dir):
    """
    Scrape data for a single team

    Args:
        team: Team dict from teams.json
        ap_rankings: Dict of AP rankings
        output_base_dir: Base directory for output (data/teams/)

    Returns:
        tuple: (team_name, success, error_message)
    """
    team_name = team['name']
    team_slug = team['slug']

    # Map team names for scraping (some teams need different names for bballnet URLs)
    scrape_name_map = {
        'UConn': 'Connecticut'
    }
    scrape_name = scrape_name_map.get(team_name, team_name)

    try:
        print(f"📥 Scraping {team_name}...")

        # Scrape team data
        team_data = scrape_team_data(scrape_name)

        if not team_data:
            return (team_name, False, "No data returned from scraper")

        # Create output directory
        output_dir = output_base_dir / team_slug
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save data
        output_prefix = str(output_dir / team_slug)
        save_team_data(team_data, output_prefix)

        return (team_name, True, None)

    except Exception as e:
        return (team_name, False, str(e))


def scrape_all_teams(max_workers=3, retry_failed=True):
    """
    Scrape data for all active teams in teams.json

    Args:
        max_workers: Number of parallel scrapers (default: 3 for respectful rate limiting)
        retry_failed: Whether to retry failed teams once

    Returns:
        dict: Results summary with successful and failed teams
    """
    print("🏀 NCAA Batch Scraper")
    print("=" * 50)

    # Load team configuration
    teams = load_teams()
    active_teams = [t for t in teams if t.get('active', True)]

    print(f"📋 Found {len(active_teams)} active teams to scrape\n")

    # Scrape AP rankings once (shared by all teams)
    print("📊 Scraping AP Poll rankings...")
    ap_rankings = scrape_ap_rankings()
    print()

    # Setup output directory
    output_base_dir = Path(__file__).parent.parent / 'data' / 'teams'
    output_base_dir.mkdir(parents=True, exist_ok=True)

    # Track results
    results = {
        'successful': [],
        'failed': []
    }

    # Scrape teams in parallel
    print(f"🔄 Scraping teams (max {max_workers} parallel)...")
    print("-" * 50)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all scraping tasks
        future_to_team = {
            executor.submit(scrape_single_team, team, ap_rankings, output_base_dir): team
            for team in active_teams
        }

        # Process completed tasks
        for future in as_completed(future_to_team):
            team_name, success, error = future.result()

            if success:
                results['successful'].append(team_name)
                print(f"  ✅ {team_name}")
            else:
                results['failed'].append((team_name, error))
                print(f"  ❌ {team_name}: {error}")

            # Small delay to be respectful to servers
            time.sleep(0.5)

    print("-" * 50)
    print()

    # Retry failed teams once if requested
    if retry_failed and results['failed']:
        print(f"🔁 Retrying {len(results['failed'])} failed teams...")
        print("-" * 50)

        failed_teams = results['failed'].copy()
        results['failed'] = []

        for team_name, _ in failed_teams:
            # Find team dict
            team = next((t for t in active_teams if t['name'] == team_name), None)
            if not team:
                continue

            print(f"📥 Retrying {team_name}...")
            time.sleep(2)  # Longer delay for retries

            name, success, error = scrape_single_team(team, ap_rankings, output_base_dir)

            if success:
                results['successful'].append(name)
                print(f"  ✅ {name}")
            else:
                results['failed'].append((name, error))
                print(f"  ❌ {name}: {error}")

        print("-" * 50)
        print()

    # Print summary
    print("📊 Scraping Summary")
    print("=" * 50)
    print(f"✅ Successful: {len(results['successful'])}/{len(active_teams)}")

    if results['failed']:
        print(f"❌ Failed: {len(results['failed'])}/{len(active_teams)}")
        print("\nFailed teams:")
        for team_name, error in results['failed']:
            print(f"  - {team_name}: {error}")
    else:
        print("🎉 All teams scraped successfully!")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Batch scrape NCAA team data')
    parser.add_argument('--workers', type=int, default=3,
                        help='Number of parallel workers (default: 3)')
    parser.add_argument('--no-retry', action='store_true',
                        help='Do not retry failed teams')

    args = parser.parse_args()

    results = scrape_all_teams(
        max_workers=args.workers,
        retry_failed=not args.no_retry
    )

    # Exit with error code if any failures
    if results['failed']:
        sys.exit(1)
