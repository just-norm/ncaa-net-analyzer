#!/usr/bin/env python3
"""
Scraper for bballnet.com - single source for NET rankings and team schedules
Also fetches AP rankings from NCAA.com
"""

import requests
from bs4 import BeautifulSoup
import csv
import re

def scrape_ap_rankings():
    """Scrape AP Poll rankings from NCAA.com"""
    url = "https://www.ncaa.com/rankings/basketball-men/d1/associated-press"

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        rankings = {}
        table = soup.find('table')

        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    rank_text = cols[0].get_text(strip=True)
                    team_text = cols[1].get_text(strip=True)

                    rank_match = re.search(r'\d+', rank_text)
                    if rank_match:
                        rank = int(rank_match.group())
                        team_name = team_text.strip()
                        rankings[team_name] = rank

        print(f"✅ Scraped {len(rankings)} teams from AP Poll")
        return rankings

    except Exception as e:
        print(f"⚠️  Could not fetch AP Poll: {e}")
        return {}

def scrape_team_data(team_name):
    """
    Scrape complete team data from bballnet.com and AP rankings from NCAA.com
    Returns: dict with team rankings, record, and schedule
    """
    # Convert team name to URL format (lowercase, replace spaces with hyphens)
    team_url = team_name.lower().replace(' ', '-')
    url = f'https://bballnet.com/teams/{team_url}'

    print(f"🏀 Scraping data for {team_name}...")
    print(f"   URL: {url}")

    # Fetch AP rankings
    ap_rankings = scrape_ap_rankings()
    ap_rank = ap_rankings.get(team_name, None)

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract team NET ranking
        net_rank = None
        rank_elements = soup.find_all('h2')
        for elem in rank_elements:
            text = elem.get_text(strip=True)
            if 'NET Ranking:' in text:
                match = re.search(r'NET Ranking:\s*(\d+)', text)
                if match:
                    net_rank = int(match.group(1))

        # Extract record
        record = None
        record_elements = soup.find_all(['p', 'div', 'span'])
        for elem in record_elements:
            text = elem.get_text(strip=True)
            match = re.search(r'Record:\s*(\d+-\d+)', text)
            if match:
                record = match.group(1)
                break

        # Extract quadrant breakdown
        quadrant_data = {}
        tables = soup.find_all('table')
        for table in tables:
            # Look for quadrant table
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            if 'Quadrant' in headers or 'Quad' in headers:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        quad = cells[0].get_text(strip=True)
                        record_text = cells[1].get_text(strip=True)
                        quadrant_data[quad] = record_text

        # Extract schedule
        schedule = []
        # Find the main schedule table
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 5:  # Likely the schedule table
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        # Try to parse game data
                        # Typical format: Result | Score/Date | Location | Opponent (NET rank) | Quad
                        try:
                            result_cell = cells[0].get_text(strip=True)
                            if result_cell in ['W', 'L']:
                                result = result_cell

                                # Score and date
                                score_date = cells[1].get_text(strip=True)
                                score_match = re.search(r'(\d+-\d+)', score_date)
                                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', score_date)

                                score = score_match.group(1) if score_match else ''
                                date = date_match.group(1) if date_match else ''

                                # Location
                                location_text = cells[2].get_text(strip=True)
                                if 'Home' in location_text:
                                    location = 'Home'
                                elif 'Away' in location_text:
                                    location = 'Away'
                                elif 'Neutral' in location_text:
                                    location = 'Neutral'
                                else:
                                    location = location_text

                                # Opponent and NET rank
                                opponent_cell = cells[3].get_text(strip=True)
                                opponent_match = re.search(r'^(.+?)\s*\((\d+)\)$', opponent_cell)
                                if opponent_match:
                                    opponent = opponent_match.group(1).strip()
                                    opp_net = int(opponent_match.group(2))
                                else:
                                    opponent = opponent_cell
                                    opp_net = None

                                # Quadrant
                                quad = cells[4].get_text(strip=True) if len(cells) > 4 else ''

                                schedule.append({
                                    'date': date,
                                    'opponent': opponent,
                                    'location': location,
                                    'result': result,
                                    'score': score,
                                    'net_rank': opp_net,
                                    'quadrant': quad
                                })
                        except (IndexError, AttributeError):
                            continue

        return {
            'team_name': team_name,
            'net_rank': net_rank,
            'ap_rank': ap_rank,
            'record': record,
            'quadrant_breakdown': quadrant_data,
            'schedule': schedule
        }

    except Exception as e:
        print(f"❌ Error scraping {team_name}: {e}")
        return None

def save_team_data(team_data, output_prefix):
    """Save team data to CSV files"""
    if not team_data or not team_data['schedule']:
        print("❌ No data to save")
        return

    team_name = team_data['team_name']

    # Save schedule
    schedule_file = f'{output_prefix}_schedule_analysis.csv'
    with open(schedule_file, 'w', newline='') as f:
        fieldnames = ['date', 'opponent', 'location', 'result', 'score', 'net_rank', 'quadrant']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(team_data['schedule'])

    print(f"✅ Saved schedule to {schedule_file}")

    # Save team rankings
    rankings_file = f'{output_prefix}_own_rankings.csv'
    with open(rankings_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['System', 'Rank'])
        writer.writerow(['NET', team_data['net_rank'] if team_data['net_rank'] else 'NR'])
        writer.writerow(['AP', team_data['ap_rank'] if team_data.get('ap_rank') else 'NR'])

    print(f"✅ Saved rankings to {rankings_file}")

    # Calculate and save location breakdown
    location_breakdown = {}
    for game in team_data['schedule']:
        if game['result'] == 'W' and game['net_rank']:
            key = (game['quadrant'], game['location'])
            if key not in location_breakdown:
                location_breakdown[key] = []
            location_breakdown[key].append(game['net_rank'])

    breakdown_file = f'{output_prefix}_location_breakdown.csv'
    with open(breakdown_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Quadrant', 'Location', 'Wins', 'Average_NET', 'Median_NET', 'NET_Ranks'])

        for quad in ['Quad 1', 'Quad 2', 'Quad 3', 'Quad 4']:
            for loc in ['Home', 'Away', 'Neutral']:
                key = (quad, loc)
                if key in location_breakdown:
                    ranks = location_breakdown[key]
                    avg_net = sum(ranks) / len(ranks)
                    median_net = sorted(ranks)[len(ranks) // 2]
                    writer.writerow([quad, loc, len(ranks), f'{avg_net:.1f}', median_net, ranks])

    print(f"✅ Saved location breakdown to {breakdown_file}")

    # Print summary
    print(f"\n📊 {team_name} Summary:")
    print(f"   NET Ranking: #{team_data['net_rank']}")
    print(f"   Record: {team_data['record']}")
    print(f"   Games played: {len(team_data['schedule'])}")

    # Count by quadrant
    quad_wins = {}
    for game in team_data['schedule']:
        if game['result'] == 'W':
            quad = game['quadrant']
            quad_wins[quad] = quad_wins.get(quad, 0) + 1

    for quad in ['Quad 1', 'Quad 2', 'Quad 3', 'Quad 4']:
        wins = quad_wins.get(quad, 0)
        print(f"   {quad}: {wins} wins")

if __name__ == "__main__":
    # Test with Michigan
    team_data = scrape_team_data('michigan')
    if team_data:
        save_team_data(team_data, 'michigan')
