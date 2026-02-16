#!/usr/bin/env python3
"""
Combined scraper using Sports-Reference for schedules and NCAA.com for NET rankings
"""

import sys
import csv
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.sports_reference_scraper import scrape_team_schedule
from scrapers.ncaa_net_scraper import scrape_net_rankings
from scrapers.bballnet_scraper import scrape_ap_rankings
from utils.quadrant_calculator import calculate_quadrant
from utils.team_name_normalizer import find_team_match


def scrape_team_complete(team_name, year=2026):
    """
    Scrape complete team data from multiple sources

    Args:
        team_name: Team name
        year: Season year

    Returns:
        dict: Complete team data with schedule, rankings, quadrants
    """
    print(f"\n🏀 Scraping complete data for {team_name}")
    print("=" * 60)

    # 1. Get schedule from Sports-Reference
    schedule = scrape_team_schedule(team_name, year)
    if not schedule:
        return None

    # 2. Get NET rankings from NCAA.com
    net_rankings = scrape_net_rankings()
    if not net_rankings:
        print("⚠️  Could not fetch NET rankings, continuing anyway...")

    # 3. Get AP rankings
    ap_rankings = scrape_ap_rankings()

    # 4. Find team's own NET and AP ranks
    team_net_match = find_team_match(team_name, net_rankings)
    team_net_rank = net_rankings[team_net_match]['rank'] if team_net_match else None

    team_ap_match = find_team_match(team_name, ap_rankings)
    team_ap_rank = ap_rankings[team_ap_match] if team_ap_match else None

    # 5. Match opponents to NET rankings and calculate quadrants
    enriched_schedule = []

    for game in schedule:
        opponent = game['opponent']
        location = game['location']

        # Find opponent's NET rank using improved name matching
        opp_net_match = find_team_match(opponent, net_rankings)
        opp_net_rank = net_rankings[opp_net_match]['rank'] if opp_net_match else None

        # Calculate quadrant
        if opp_net_rank:
            quadrant = calculate_quadrant(opp_net_rank, location)
        else:
            quadrant = 'Q4'  # Default for unranked teams

        enriched_schedule.append({
            'date': game['date'],
            'opponent': opponent,
            'location': location,
            'result': game['result'],
            'score': game['score'],
            'net_rank': opp_net_rank if opp_net_rank else '',
            'ap_rank': 'NR',
            'quadrant': quadrant
        })

    print(f"\n📊 Summary:")
    print(f"   Team NET: #{team_net_rank if team_net_rank else 'NR'}")
    print(f"   Team AP: #{team_ap_rank if team_ap_rank else 'NR'}")
    print(f"   Games: {len(enriched_schedule)}")

    # Count quadrant wins
    quad_wins = {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0}
    for game in enriched_schedule:
        if game['result'] == 'W' and game['quadrant'] in quad_wins:
            quad_wins[game['quadrant']] += 1

    print(f"   Wins: Q1={quad_wins['Q1']}, Q2={quad_wins['Q2']}, Q3={quad_wins['Q3']}, Q4={quad_wins['Q4']}")

    return {
        'team_name': team_name,
        'net_rank': team_net_rank,
        'ap_rank': team_ap_rank,
        'schedule': enriched_schedule
    }


def save_team_data(team_data, output_dir):
    """
    Save team data to CSV files

    Args:
        team_data: Complete team data dict
        output_dir: Output directory path
    """
    if not team_data or not team_data['schedule']:
        print("❌ No data to save")
        return False

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    team_slug = output_path.name

    # Save schedule
    schedule_file = output_path / f'{team_slug}_schedule_analysis.csv'
    with open(schedule_file, 'w', newline='') as f:
        fieldnames = ['date', 'opponent', 'location', 'result', 'score', 'net_rank', 'ap_rank', 'quadrant']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(team_data['schedule'])

    print(f"✅ Saved schedule: {schedule_file}")

    # Save rankings
    rankings_file = output_path / f'{team_slug}_own_rankings.csv'
    with open(rankings_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['System', 'Rank'])
        writer.writerow(['NET', team_data['net_rank'] if team_data['net_rank'] else 'NR'])
        writer.writerow(['AP', team_data['ap_rank'] if team_data['ap_rank'] else 'NR'])

    print(f"✅ Saved rankings: {rankings_file}")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python combined_scraper.py <team-name>")
        print("Example: python combined_scraper.py Michigan")
        sys.exit(1)

    team_name = ' '.join(sys.argv[1:])
    team_data = scrape_team_complete(team_name)

    if team_data:
        # Save to data/teams/{team-slug}/
        team_slug = team_name.lower().replace(' ', '-')
        output_dir = Path(__file__).parent.parent / 'data' / 'teams' / team_slug
        save_team_data(team_data, output_dir)
        print(f"\n✅ Complete! Data saved to {output_dir}")
    else:
        print(f"\n❌ Failed to scrape {team_name}")
        sys.exit(1)
