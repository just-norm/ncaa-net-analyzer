#!/usr/bin/env python3
"""
Simple bballnet.com scraper using requests + BeautifulSoup
Extracts team data including NET ranking, record, and schedule
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime

def scrape_bballnet_team(team_slug):
    """
    Scrape team data from bballnet.com
    team_slug: lowercase team name with hyphens (e.g., 'michigan', 'arizona')
    """
    url = f'https://bballnet.com/teams/{team_slug}'

    print(f"🏀 Scraping {team_slug} from bballnet.com...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract NET ranking and record from text
        page_text = soup.get_text()

        # Find NET ranking
        net_match = re.search(r'NET:\s*(\d+)', page_text)
        net_rank = int(net_match.group(1)) if net_match else None

        # Find record
        record_match = re.search(r'Record:\s*(\d+-\d+)', page_text)
        record = record_match.group(1) if record_match else None

        # Find quadrant records
        quad_records = {}
        for quad_num in [1, 2, 3, 4]:
            pattern = f'Quad {quad_num}.*?Record:\\s*(\\d+-\\d+)'
            match = re.search(pattern, page_text, re.DOTALL)
            if match:
                quad_records[f'Quad {quad_num}'] = match.group(1)

        # Find all game rows in tables
        schedule = []
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:  # Should have: Result, Score/Date, Location, Opponent, Quad
                    try:
                        # Result (W/L)
                        result_text = cells[0].get_text(strip=True)
                        if 'W' in result_text:
                            result = 'W'
                        elif 'L' in result_text:
                            result = 'L'
                        else:
                            continue

                        # Score and date
                        score_date_text = cells[1].get_text(strip=True)
                        score_match = re.search(r'(\\d+-\\d+)', score_date_text)
                        date_match = re.search(r'(\\d{1,2}/\\d{1,2}/\\d{4})', score_date_text)

                        score = score_match.group(1) if score_match else ''
                        if date_match:
                            # Convert date from MM/DD/YYYY to "Mon DD" format
                            date_obj = datetime.strptime(date_match.group(1), '%m/%d/%Y')
                            date = date_obj.strftime('%b %d')
                        else:
                            date = ''

                        # Location
                        location_text = cells[2].get_text(strip=True)
                        if 'Home' in location_text:
                            location = 'Home'
                        elif 'Away' in location_text:
                            location = 'Away'
                        elif 'Neutral' in location_text:
                            location = 'Neutral'
                        else:
                            location = 'Home'  # default

                        # Opponent and NET rank
                        opponent_text = cells[3].get_text(strip=True)
                        # Format is usually: "Team Name (NET)"
                        opp_match = re.match(r'^(.+?)\\s*\\((\\d+)\\)$', opponent_text)
                        if opp_match:
                            opponent = opp_match.group(1).strip()
                            net_rank_opp = int(opp_match.group(2))
                        else:
                            opponent = opponent_text
                            net_rank_opp = 'N/A'

                        # Quadrant
                        quadrant_text = cells[4].get_text(strip=True) if len(cells) > 4 else ''
                        # Convert "Quad 1" to "Q1"
                        quad_match = re.search(r'Quad\\s*(\\d)', quadrant_text)
                        if quad_match:
                            quadrant = f'Q{quad_match.group(1)}'
                        else:
                            quadrant = quadrant_text

                        schedule.append({
                            'date': date,
                            'opponent': opponent,
                            'location': location,
                            'result': result,
                            'score': score,
                            'net_rank': net_rank_opp,
                            'quadrant': quadrant
                        })

                    except (IndexError, ValueError, AttributeError) as e:
                        continue

        return {
            'team_slug': team_slug,
            'net_rank': net_rank,
            'record': record,
            'quad_records': quad_records,
            'schedule': schedule
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_team_csvs(team_data, output_prefix):
    """Save team data to CSV files matching our existing format"""
    if not team_data:
        print("❌ No data to save")
        return

    # Save schedule
    with open(f'{output_prefix}_schedule_analysis.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'opponent', 'location', 'result', 'score', 'net_rank', 'ap_rank', 'quadrant'])
        writer.writeheader()
        for game in team_data['schedule']:
            game['ap_rank'] = 'NR'  # bballnet doesn't have AP ranks
            writer.writerow(game)

    # Save rankings
    with open(f'{output_prefix}_own_rankings.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['System', 'Rank'])
        writer.writerow(['NET', team_data['net_rank'] if team_data['net_rank'] else 'NR'])
        writer.writerow(['AP', 'NR'])  # Would need to scrape separately

    # Save location breakdown
    location_breakdown = {}
    for game in team_data['schedule']:
        if game['result'] == 'W' and game['net_rank'] != 'N/A':
            key = (game['quadrant'], game['location'])
            if key not in location_breakdown:
                location_breakdown[key] = []
            location_breakdown[key].append(int(game['net_rank']))

    with open(f'{output_prefix}_location_breakdown.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Quadrant', 'Location', 'Wins', 'Average_NET', 'Median_NET', 'NET_Ranks'])

        for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
            for loc in ['Home', 'Away', 'Neutral']:
                key = (quad, loc)
                if key in location_breakdown:
                    ranks = location_breakdown[key]
                    avg_net = sum(ranks) / len(ranks)
                    median_net = sorted(ranks)[len(ranks) // 2]
                    writer.writerow([quad, loc, len(ranks), f'{avg_net:.1f}', median_net, ranks])

    # Print summary
    wins = sum(1 for g in team_data['schedule'] if g['result'] == 'W')
    losses = sum(1 for g in team_data['schedule'] if g['result'] == 'L')

    print(f"\n✅ {team_data['team_slug'].title()} Data Saved!")
    print(f"   NET Rank: #{team_data['net_rank']}")
    print(f"   Record: {team_data['record']} ({wins}-{losses} from schedule)")
    print(f"   Total games: {len(team_data['schedule'])}")

    quad_wins = {}
    for game in team_data['schedule']:
        if game['result'] == 'W':
            q = game['quadrant']
            quad_wins[q] = quad_wins.get(q, 0) + 1

    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        print(f"   {quad}: {quad_wins.get(quad, 0)} wins")

if __name__ == "__main__":
    import sys

    team = sys.argv[1] if len(sys.argv) > 1 else 'michigan'
    team_data = scrape_bballnet_team(team)

    if team_data:
        save_team_csvs(team_data, team)
