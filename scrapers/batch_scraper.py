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

from scrapers.combined_scraper import scrape_team_complete, save_team_data
from utils.team_config import load_teams


def scrape_single_team(team, output_base_dir):
    """
    Scrape data for a single team using combined scraper

    Args:
        team: Team dict from teams.json
        output_base_dir: Base directory for output (data/teams/)

    Returns:
        tuple: (team_name, success, error_message)
    """
    team_name = team['name']
    team_slug = team['slug']

    try:
        print(f"📥 Scraping {team_name}...")

        # Scrape team data using combined scraper
        team_data = scrape_team_complete(team_name, year=2026)

        if not team_data:
            return (team_name, False, "No data returned from scraper")

        # Create output directory
        output_dir = output_base_dir / team_slug

        # Save data
        success = save_team_data(team_data, output_dir)

        if not success:
            return (team_name, False, "Failed to save data")

        return (team_name, True, None)

    except Exception as e:
        return (team_name, False, str(e))


def scrape_all_teams(max_workers=3, retry_failed=True, batch_size=None, delay=1):
    """
    Scrape data for all active teams in teams.json

    Args:
        max_workers: Number of parallel scrapers (default: 3 for respectful rate limiting)
        retry_failed: Whether to retry failed teams once
        batch_size: Maximum number of teams to scrape (None = all teams)
        delay: Delay in seconds between teams (default: 1)

    Returns:
        dict: Results summary with successful and failed teams
    """
    print("🏀 NCAA Batch Scraper")
    print("=" * 50)

    # Load team configuration
    teams = load_teams()
    active_teams = [t for t in teams if t.get('active', True)]

    # Setup output directory
    output_base_dir = Path(__file__).parent.parent / 'data' / 'teams'
    output_base_dir.mkdir(parents=True, exist_ok=True)

    # Filter out teams that already have data
    teams_to_scrape = []
    already_scraped = []

    for team in active_teams:
        team_slug = team['slug']
        # Check for the file that combined_scraper actually creates
        schedule_file = output_base_dir / team_slug / f'{team_slug}_schedule_analysis.csv'

        if schedule_file.exists():
            already_scraped.append(team['name'])
        else:
            teams_to_scrape.append(team)

    print(f"📋 Total teams: {len(active_teams)}")
    print(f"✅ Already scraped: {len(already_scraped)}")
    print(f"📥 Need to scrape: {len(teams_to_scrape)}")

    # Apply batch size limit (teams are already sorted by NET ranking in teams.json)
    if batch_size and len(teams_to_scrape) > batch_size:
        print(f"🎯 Limiting to batch size: {batch_size} teams")
        teams_to_scrape = teams_to_scrape[:batch_size]

    if not teams_to_scrape:
        print("🎉 All teams already scraped!")
        return {'successful': already_scraped, 'failed': []}

    print(f"🔄 Scraping {len(teams_to_scrape)} teams this run\n")

    # Track results
    results = {
        'successful': already_scraped.copy(),  # Include already-scraped teams
        'failed': []
    }

    # Scrape teams sequentially (combined scraper handles all data sources)
    print(f"🔄 Scraping teams (sequential, {delay}s delay)...")
    print("-" * 50)

    for i, team in enumerate(teams_to_scrape, 1):
        print(f"\n[{i}/{len(teams_to_scrape)}] ", end='')

        team_name, success, error = scrape_single_team(team, output_base_dir)

        if success:
            results['successful'].append(team_name)
            print(f"  ✅ {team_name}")
        else:
            results['failed'].append((team_name, error))
            print(f"  ❌ {team_name}: {error}")

        # Configurable delay to be respectful to servers
        if i < len(teams_to_scrape):  # Don't delay after last team
            time.sleep(delay)

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
            team = next((t for t in teams_to_scrape if t['name'] == team_name), None)
            if not team:
                continue

            print(f"📥 Retrying {team_name}...")
            time.sleep(delay * 2)  # Longer delay for retries

            name, success, error = scrape_single_team(team, output_base_dir)

            if success:
                results['successful'].append(name)
                print(f"  ✅ {name}")
            else:
                results['failed'].append((name, error))
                print(f"  ❌ {name}: {error}")

        print("-" * 50)
        print()

    # Print summary
    total_attempted = len(teams_to_scrape)
    newly_scraped = len(results['successful']) - len(already_scraped)

    print("📊 Scraping Summary")
    print("=" * 50)
    print(f"📥 Attempted this run: {total_attempted}")
    print(f"✅ Successfully scraped: {newly_scraped}")
    print(f"💾 Total teams with data: {len(results['successful'])}/{len(active_teams)}")

    if results['failed']:
        print(f"❌ Failed this run: {len(results['failed'])}")
        print("\nFailed teams:")
        for team_name, error in results['failed']:
            print(f"  - {team_name}: {error}")
    elif total_attempted > 0:
        print("🎉 All attempted teams scraped successfully!")

    if len(results['successful']) == len(active_teams):
        print("\n🏆 All teams complete!")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Batch scrape NCAA team data')
    parser.add_argument('--workers', type=int, default=1,
                        help='Number of parallel workers (default: 1 for sequential)')
    parser.add_argument('--batch-size', type=int, default=None,
                        help='Maximum number of teams to scrape (default: all unscraped teams)')
    parser.add_argument('--delay', type=int, default=1,
                        help='Delay in seconds between teams (default: 1)')
    parser.add_argument('--no-retry', action='store_true',
                        help='Do not retry failed teams')

    args = parser.parse_args()

    results = scrape_all_teams(
        max_workers=args.workers,
        retry_failed=not args.no_retry,
        batch_size=args.batch_size,
        delay=args.delay
    )

    # Only exit with error if NO teams were scraped AND there were failures
    # This allows successful data to be committed even when some teams fail
    if results['failed'] and not results['successful']:
        print("\n❌ No teams were successfully scraped")
        sys.exit(1)
