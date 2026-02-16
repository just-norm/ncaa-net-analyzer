#!/usr/bin/env python3
"""
NCAA NET Rankings Analyzer for University of Arizona
Scrapes NET rankings and analyzes Arizona's 2025-26 schedule
"""

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def scrape_net_rankings():
    """Scrape current NET rankings from NCAA.com"""
    url = 'https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings'

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all team rows in the rankings table
        rankings = {}
        rows = soup.find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                try:
                    rank = int(cells[0].get_text(strip=True))
                    team_name = cells[1].get_text(strip=True)
                    rankings[team_name] = rank
                except ValueError:
                    continue

        print(f"✅ Scraped {len(rankings)} teams from NET rankings")
        return rankings

    except Exception as e:
        print(f"❌ Error scraping NET rankings: {e}")
        return {}

def scrape_ap_poll():
    """Scrape AP Poll rankings from NCAA.com"""
    url = 'https://www.ncaa.com/rankings/basketball-men/d1/associated-press'

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        ap_rankings = {}
        rows = soup.find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                try:
                    rank = int(cells[0].get_text(strip=True))
                    team_name = cells[1].get_text(strip=True)
                    ap_rankings[team_name] = rank
                except ValueError:
                    continue

        print(f"✅ Scraped {len(ap_rankings)} teams from AP Poll")
        return ap_rankings

    except Exception as e:
        print(f"❌ Error scraping AP Poll: {e}")
        return {}

def normalize_team_name(name):
    """Normalize team names for matching"""
    # Common name mappings
    team_name_map = {
        'USC': 'Southern California',
        'Middle Tennessee': 'Middle Tenn.',
        'Michigan State': 'Michigan St.',
        'Ohio State': 'Ohio St.',
        'San Diego State': 'San Diego St.',
        'Penn State': 'Penn St.',
        'Oklahoma State': 'Oklahoma St.',
        'Iowa State': 'Iowa St.',
        'Kansas State': 'Kansas St.',
        'Ole Miss': 'Mississippi',
        'Mississippi State': 'Mississippi St.',
        'NC State': 'N.C. State',
        'TCU': 'TCU',
        'Brigham Young': 'BYU',
        'UCLA': 'UCLA',
        'UNLV': 'UNLV',
        'SMU': 'SMU',
        'UCF': 'UCF',
        'Arizona State': 'Arizona St.',
        'Oregon State': 'Oregon St.',
        'Washington State': 'Washington St.',
        'Connecticut': 'UConn',
        'South Dakota State': 'South Dakota St.',
        'Northern Arizona': 'Northern Ariz.',
        'Norfolk State': 'Norfolk St.',
    }

    return team_name_map.get(name, name)

def find_team_rank(team_name, rankings):
    """Find team's NET ranking with fuzzy matching"""
    normalized = normalize_team_name(team_name)

    # Try exact match first
    if normalized in rankings:
        return rankings[normalized]

    # Try case-insensitive match
    for rank_team, rank in rankings.items():
        if rank_team.lower() == normalized.lower():
            return rank

    # Try word-based partial match (more strict to avoid substring issues)
    normalized_lower = normalized.lower()
    for rank_team, rank in rankings.items():
        rank_team_lower = rank_team.lower()
        # Only match if the words are similar, not just substrings
        # This prevents "Arizona" from matching "Northern Arizona"
        if normalized_lower == rank_team_lower:
            return rank
        # Check if one is an abbreviation of the other (e.g., "St." vs "State")
        if normalized_lower.replace('state', 'st.').replace('st.', 'state') == rank_team_lower.replace('state', 'st.').replace('st.', 'state'):
            return rank

    return None

def determine_quadrant(net_rank, location):
    """Determine quadrant based on NET rank and game location"""
    if location == 'Home':
        if net_rank <= 30:
            return 'Q1'
        elif net_rank <= 75:
            return 'Q2'
        elif net_rank <= 160:
            return 'Q3'
        else:
            return 'Q4'
    elif location == 'Away':
        if net_rank <= 75:
            return 'Q1'
        elif net_rank <= 135:
            return 'Q2'
        elif net_rank <= 240:
            return 'Q3'
        else:
            return 'Q4'
    else:  # Neutral
        if net_rank <= 50:
            return 'Q1'
        elif net_rank <= 100:
            return 'Q2'
        elif net_rank <= 200:
            return 'Q3'
        else:
            return 'Q4'

def get_arizona_schedule():
    """
    Arizona's 2025-26 schedule
    Data from Sports-Reference for accurate location information
    """
    schedule = [
        {'date': 'Nov 3', 'opponent': 'Florida', 'location': 'Neutral', 'result': 'W', 'score': '93-87'},
        {'date': 'Nov 7', 'opponent': 'Utah Tech', 'location': 'Home', 'result': 'W', 'score': '93-67'},
        {'date': 'Nov 11', 'opponent': 'Northern Arizona', 'location': 'Home', 'result': 'W', 'score': '84-49'},
        {'date': 'Nov 14', 'opponent': 'UCLA', 'location': 'Neutral', 'result': 'W', 'score': '69-65'},
        {'date': 'Nov 19', 'opponent': 'Connecticut', 'location': 'Away', 'result': 'W', 'score': '71-67'},
        {'date': 'Nov 24', 'opponent': 'Denver', 'location': 'Home', 'result': 'W', 'score': '103-73'},
        {'date': 'Nov 29', 'opponent': 'Norfolk State', 'location': 'Home', 'result': 'W', 'score': '98-61'},
        {'date': 'Dec 6', 'opponent': 'Auburn', 'location': 'Home', 'result': 'W', 'score': '97-68'},
        {'date': 'Dec 13', 'opponent': 'Alabama', 'location': 'Neutral', 'result': 'W', 'score': '96-75'},
        {'date': 'Dec 16', 'opponent': 'Abilene Christian', 'location': 'Home', 'result': 'W', 'score': '96-62'},
        {'date': 'Dec 20', 'opponent': 'San Diego State', 'location': 'Neutral', 'result': 'W', 'score': '68-45'},
        {'date': 'Dec 22', 'opponent': 'Bethune-Cookman', 'location': 'Home', 'result': 'W', 'score': '107-71'},
        {'date': 'Dec 29', 'opponent': 'South Dakota State', 'location': 'Home', 'result': 'W', 'score': '99-71'},
        {'date': 'Jan 3', 'opponent': 'Utah', 'location': 'Away', 'result': 'W', 'score': '97-78'},
        {'date': 'Jan 7', 'opponent': 'Kansas State', 'location': 'Home', 'result': 'W', 'score': '101-76'},
        {'date': 'Jan 10', 'opponent': 'TCU', 'location': 'Away', 'result': 'W', 'score': '86-73'},
        {'date': 'Jan 14', 'opponent': 'Arizona State', 'location': 'Home', 'result': 'W', 'score': '89-82'},
        {'date': 'Jan 17', 'opponent': 'UCF', 'location': 'Away', 'result': 'W', 'score': '84-77'},
        {'date': 'Jan 21', 'opponent': 'Cincinnati', 'location': 'Home', 'result': 'W', 'score': '77-51'},
        {'date': 'Jan 24', 'opponent': 'West Virginia', 'location': 'Home', 'result': 'W', 'score': '88-53'},
        {'date': 'Jan 26', 'opponent': 'Brigham Young', 'location': 'Away', 'result': 'W', 'score': '86-83'},
        {'date': 'Jan 31', 'opponent': 'Arizona State', 'location': 'Away', 'result': 'W', 'score': '87-74'},
        {'date': 'Feb 7', 'opponent': 'Oklahoma State', 'location': 'Home', 'result': 'W', 'score': '84-47'},
        {'date': 'Feb 9', 'opponent': 'Kansas', 'location': 'Away', 'result': 'L', 'score': '78-82'},
        {'date': 'Feb 14', 'opponent': 'Texas Tech', 'location': 'Home', 'result': 'L', 'score': '75-78'},
    ]

    return schedule

def analyze_arizona_schedule():
    """Analyze Arizona's schedule with NET rankings"""
    print("🏀 NCAA NET Rankings Analyzer - University of Arizona")
    print("=" * 60)

    # Get NET rankings
    net_rankings = scrape_net_rankings()
    ap_rankings = scrape_ap_poll()

    if not net_rankings:
        print("❌ Failed to get NET rankings")
        return

    # Get Arizona's schedule
    schedule = get_arizona_schedule()

    # Get Arizona's own rankings
    arizona_net = find_team_rank('Arizona', net_rankings)
    arizona_ap = find_team_rank('Arizona', ap_rankings)

    print(f"\n📊 Arizona Rankings:")
    print(f"   NET: #{arizona_net if arizona_net else 'NR'}")
    print(f"   AP: #{arizona_ap if arizona_ap else 'NR'}")

    # Save Arizona's rankings
    with open('arizona_own_rankings.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['System', 'Rank'])
        writer.writerow(['NET', arizona_net if arizona_net else 'NR'])
        writer.writerow(['AP', arizona_ap if arizona_ap else 'NR'])

        # Calculate average (only for ranked teams)
        ranks = []
        if arizona_net:
            ranks.append(arizona_net)
        if arizona_ap:
            ranks.append(arizona_ap)

        if ranks:
            avg = sum(ranks) / len(ranks)
            writer.writerow(['Average', f'{avg:.1f}'])
        else:
            writer.writerow(['Average', 'N/A'])

    # Analyze each game
    analyzed_games = []
    quadrant_stats = {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []}
    location_breakdown = {}

    for game in schedule:
        opponent = game['opponent']
        location = game['location']
        result = game['result']

        # Find opponent's NET ranking
        net_rank = find_team_rank(opponent, net_rankings)
        ap_rank = find_team_rank(opponent, ap_rankings)

        if net_rank is None:
            print(f"⚠️  Could not find NET ranking for {opponent}")
            net_rank = 'N/A'
            quadrant = 'N/A'
        else:
            quadrant = determine_quadrant(net_rank, location)

            # Track stats for wins
            if result == 'W':
                quadrant_stats[quadrant].append(net_rank)

                # Track location breakdown
                key = (quadrant, location)
                if key not in location_breakdown:
                    location_breakdown[key] = []
                location_breakdown[key].append(net_rank)

        analyzed_games.append({
            'date': game['date'],
            'opponent': opponent,
            'location': location,
            'result': result,
            'score': game['score'],
            'net_rank': net_rank,
            'ap_rank': ap_rank if ap_rank else 'NR',
            'quadrant': quadrant
        })

    # Save to CSV
    with open('arizona_schedule_analysis.csv', 'w', newline='') as f:
        fieldnames = ['date', 'opponent', 'location', 'result', 'score', 'net_rank', 'ap_rank', 'quadrant']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(analyzed_games)

    # Save location breakdown
    with open('arizona_location_breakdown.csv', 'w', newline='') as f:
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
    print("\n📈 Quadrant Summary:")
    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        wins = quadrant_stats[quad]
        if wins:
            avg = sum(wins) / len(wins)
            median = sorted(wins)[len(wins) // 2]
            print(f"   {quad}: {len(wins)} wins (Avg NET: {avg:.1f}, Median: {median})")
        else:
            print(f"   {quad}: 0 wins")

    print("\n✅ Analysis complete!")
    print(f"   - Schedule saved to arizona_schedule_analysis.csv")
    print(f"   - Location breakdown saved to arizona_location_breakdown.csv")
    print(f"   - Rankings saved to arizona_own_rankings.csv")

if __name__ == "__main__":
    analyze_arizona_schedule()
