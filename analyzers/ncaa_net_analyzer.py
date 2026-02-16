#!/usr/bin/env python3
"""
NCAA NET Rankings Analyzer
Scrapes NET rankings and team schedules to calculate average NET rank by quadrant
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime

# Quadrant definitions based on NET rank and location
# Q1: Home 1-30, Neutral 1-50, Away 1-75
# Q2: Home 31-75, Neutral 51-100, Away 76-135
# Q3: Home 76-160, Neutral 101-200, Away 136-240
# Q4: Everything else

def determine_quadrant(net_rank, location):
    """Determine the quadrant based on NET rank and game location"""
    if location == 'Home':
        if 1 <= net_rank <= 30:
            return 'Q1'
        elif 31 <= net_rank <= 75:
            return 'Q2'
        elif 76 <= net_rank <= 160:
            return 'Q3'
        else:
            return 'Q4'
    elif location == 'Away':
        if 1 <= net_rank <= 75:
            return 'Q1'
        elif 76 <= net_rank <= 135:
            return 'Q2'
        elif 136 <= net_rank <= 240:
            return 'Q3'
        else:
            return 'Q4'
    else:  # Neutral
        if 1 <= net_rank <= 50:
            return 'Q1'
        elif 51 <= net_rank <= 100:
            return 'Q2'
        elif 101 <= net_rank <= 200:
            return 'Q3'
        else:
            return 'Q4'

def scrape_net_rankings():
    """Scrape NET rankings from NCAA.com"""
    url = "https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the rankings table
        rankings = {}
        table = soup.find('table')

        if table:
            rows = table.find_all('tr')[1:]  # Skip header row

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    rank_text = cols[0].get_text(strip=True)
                    team_text = cols[1].get_text(strip=True)

                    # Extract numeric rank
                    rank_match = re.search(r'\d+', rank_text)
                    if rank_match:
                        rank = int(rank_match.group())
                        # Clean team name
                        team_name = team_text.strip()
                        rankings[team_name] = rank

        print(f"✓ Scraped {len(rankings)} teams from NET rankings")
        return rankings

    except Exception as e:
        print(f"✗ Error scraping NET rankings: {e}")
        return {}

def scrape_ap_poll():
    """Scrape AP Poll rankings"""
    url = "https://www.ncaa.com/rankings/basketball-men/d1/associated-press"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        rankings = {}
        table = soup.find('table')

        if table:
            rows = table.find_all('tr')[1:]

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

        print(f"✓ Scraped {len(rankings)} teams from AP Poll")
        return rankings

    except Exception as e:
        print(f"✗ Error scraping AP Poll: {e}")
        return {}

def scrape_coaches_poll():
    """Scrape USA Today Coaches Poll"""
    url = "https://www.ncaa.com/rankings/basketball-men/d1/usa-today-coaches"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        rankings = {}
        table = soup.find('table')

        if table:
            rows = table.find_all('tr')[1:]

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

        print(f"✓ Scraped {len(rankings)} teams from Coaches Poll")
        return rankings

    except Exception as e:
        print(f"✗ Error scraping Coaches Poll: {e}")
        return {}

def scrape_kenpom():
    """Scrape KenPom rankings"""
    url = "https://kenpom.com/"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        rankings = {}
        # KenPom uses a table with id="ratings-table"
        table = soup.find('table', {'id': 'ratings-table'})

        if table:
            rows = table.find_all('tr')[1:]  # Skip header

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    rank_text = cols[0].get_text(strip=True)
                    team_elem = cols[1].find('a')

                    if team_elem:
                        team_text = team_elem.get_text(strip=True)
                        rank_match = re.search(r'\d+', rank_text)

                        if rank_match:
                            rank = int(rank_match.group())
                            team_name = team_text.strip()
                            rankings[team_name] = rank

        print(f"✓ Scraped {len(rankings)} teams from KenPom")
        return rankings

    except Exception as e:
        print(f"✗ Error scraping KenPom: {e}")
        return {}

def scrape_torvik():
    """Scrape T-Rank (Barttorvik) rankings"""
    url = "https://barttorvik.com/trank.php"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        rankings = {}
        table = soup.find('table')

        if table:
            rows = table.find_all('tr')[1:]

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

        print(f"✓ Scraped {len(rankings)} teams from T-Rank (Torvik)")
        return rankings

    except Exception as e:
        print(f"✗ Error scraping T-Rank: {e}")
        return {}

def scrape_evanmiya():
    """Scrape EvanMiya rankings"""
    url = "https://evanmiya.com/"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        rankings = {}
        table = soup.find('table')

        if table:
            rows = table.find_all('tr')[1:]

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

        print(f"✓ Scraped {len(rankings)} teams from EvanMiya")
        return rankings

    except Exception as e:
        print(f"✗ Error scraping EvanMiya: {e}")
        return {}

def normalize_team_name(name):
    """Normalize team names for matching"""
    # Remove common prefixes/suffixes and standardize
    name = name.lower().strip()

    # Handle common variations
    replacements = {
        'st.': 'st',
        'state': 'st',
        'university': '',
        'the': '',
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    name = ' '.join(name.split())  # Remove extra spaces
    return name

def find_net_rank(team_name, net_rankings):
    """Find NET ranking for a team with fuzzy matching"""

    # Team name mapping: schedule name -> NET ranking name
    # Use this to handle mismatches between data sources
    team_name_map = {
        'USC': 'Southern California',
        'Middle Tennessee': 'Middle Tenn.',
        'Middle Tenn.': 'Middle Tenn.',
        'McNeese': 'McNeese',
        'Penn State': 'Penn St.',
        'Michigan State': 'Michigan St.',
        'Ohio State': 'Ohio St.',
        'San Diego State': 'San Diego St.',
        'Iowa State': 'Iowa St.',
        'Kansas State': 'Kansas St.',
        'Oklahoma State': 'Oklahoma St.',
        'Oregon State': 'Oregon St.',
        'Washington State': 'Washington St.',
        'Arizona State': 'Arizona St.',
        'Colorado State': 'Colorado St.',
        'Boise State': 'Boise St.',
        'Fresno State': 'Fresno St.',
        'Utah State': 'Utah St.',
    }

    # Check mapping first
    if team_name in team_name_map:
        team_name = team_name_map[team_name]

    # Try exact match
    if team_name in net_rankings:
        return net_rankings[team_name]

    # Common team name variations
    variations = [
        team_name,
        team_name.replace('State', 'St.'),
        team_name.replace('St.', 'State'),
        team_name.replace(' St', ' State'),
    ]

    for variation in variations:
        if variation in net_rankings:
            return net_rankings[variation]

    # Try normalized matching with stricter rules
    normalized_search = normalize_team_name(team_name)

    best_match = None
    best_match_rank = None

    for net_team, rank in net_rankings.items():
        normalized_net = normalize_team_name(net_team)

        # Exact match after normalization
        if normalized_search == normalized_net:
            return rank

        # Only match if search term is a complete word in the NET team name
        # This prevents "Michigan" from matching "Michigan State"
        words_search = set(normalized_search.split())
        words_net = set(normalized_net.split())

        # If all words from search are in NET team, and lengths are similar
        if words_search.issubset(words_net) and len(words_search) >= len(words_net) - 1:
            if best_match is None or len(normalized_net) < len(best_match):
                best_match = normalized_net
                best_match_rank = rank

    return best_match_rank

# Michigan's 2025-26 schedule data
# Location data from Sports-Reference (more accurate for neutral sites)
michigan_schedule = [
    {'date': 'Nov 3', 'opponent': 'Oakland', 'location': 'Home', 'result': 'W', 'score': '121-78'},
    {'date': 'Nov 11', 'opponent': 'Wake Forest', 'location': 'Home', 'result': 'W', 'score': '85-84'},
    {'date': 'Nov 14', 'opponent': 'TCU', 'location': 'Away', 'result': 'W', 'score': '67-63'},
    {'date': 'Nov 19', 'opponent': 'Middle Tenn.', 'location': 'Home', 'result': 'W', 'score': '86-61'},
    {'date': 'Nov 24', 'opponent': 'San Diego State', 'location': 'Neutral', 'result': 'W', 'score': '94-54'},
    {'date': 'Nov 25', 'opponent': 'Auburn', 'location': 'Neutral', 'result': 'W', 'score': '102-72'},
    {'date': 'Nov 26', 'opponent': 'Gonzaga', 'location': 'Neutral', 'result': 'W', 'score': '101-61'},
    {'date': 'Dec 6', 'opponent': 'Rutgers', 'location': 'Home', 'result': 'W', 'score': '101-60'},
    {'date': 'Dec 9', 'opponent': 'Villanova', 'location': 'Home', 'result': 'W', 'score': '89-61'},
    {'date': 'Dec 13', 'opponent': 'Maryland', 'location': 'Away', 'result': 'W', 'score': '101-83'},
    {'date': 'Dec 21', 'opponent': 'La Salle', 'location': 'Home', 'result': 'W', 'score': '102-50'},
    {'date': 'Dec 29', 'opponent': 'McNeese', 'location': 'Home', 'result': 'W', 'score': '112-71'},
    {'date': 'Jan 2', 'opponent': 'USC', 'location': 'Home', 'result': 'W', 'score': '96-66'},
    {'date': 'Jan 6', 'opponent': 'Penn State', 'location': 'Away', 'result': 'W', 'score': '74-72'},
    {'date': 'Jan 10', 'opponent': 'Wisconsin', 'location': 'Home', 'result': 'L', 'score': '91-88'},
    {'date': 'Jan 14', 'opponent': 'Washington', 'location': 'Away', 'result': 'W', 'score': '82-72'},
    {'date': 'Jan 17', 'opponent': 'Oregon', 'location': 'Away', 'result': 'W', 'score': '81-71'},
    {'date': 'Jan 20', 'opponent': 'Indiana', 'location': 'Home', 'result': 'W', 'score': '86-72'},
    {'date': 'Jan 23', 'opponent': 'Ohio State', 'location': 'Home', 'result': 'W', 'score': '74-62'},
    {'date': 'Jan 27', 'opponent': 'Nebraska', 'location': 'Home', 'result': 'W', 'score': '75-72'},
    {'date': 'Jan 30', 'opponent': 'Michigan State', 'location': 'Away', 'result': 'W', 'score': '83-71'},
    {'date': 'Feb 5', 'opponent': 'Penn State', 'location': 'Home', 'result': 'W', 'score': '110-69'},
    {'date': 'Feb 8', 'opponent': 'Ohio State', 'location': 'Away', 'result': 'W', 'score': '82-61'},
    {'date': 'Feb 11', 'opponent': 'Northwestern', 'location': 'Away', 'result': 'W', 'score': '87-75'},
    {'date': 'Feb 14', 'opponent': 'UCLA', 'location': 'Home', 'result': 'W', 'score': '86-56'},
]

def analyze_schedule():
    """Main analysis function"""
    print("NCAA Multi-Rankings Analyzer - University of Michigan")
    print("=" * 60)

    # Scrape all ranking systems
    print("\nScraping rankings from multiple sources...")
    print("-" * 60)

    net_rankings = scrape_net_rankings()
    ap_rankings = scrape_ap_poll()
    coaches_rankings = scrape_coaches_poll()
    kenpom_rankings = scrape_kenpom()
    torvik_rankings = scrape_torvik()
    evanmiya_rankings = scrape_evanmiya()

    all_rankings = {
        'NET': net_rankings,
        'AP': ap_rankings,
        'Coaches': coaches_rankings,
        'KenPom': kenpom_rankings,
        'Torvik': torvik_rankings,
        'EvanMiya': evanmiya_rankings
    }

    if not net_rankings:
        print("\n⚠️  Failed to scrape NET rankings. Using sample data for demonstration.")
        # Fallback to manual data if scraping fails
        net_rankings = {
            'Michigan': 1, 'Duke': 2, 'Arizona': 3, 'Houston': 4, 'Purdue': 5,
            'Gonzaga': 6, 'Illinois': 7, 'Iowa St.': 8, 'Florida': 9, 'UConn': 10,
            'Nebraska': 11, 'Michigan St.': 15, 'Villanova': 30, 'Indiana': 31,
            'Wisconsin': 33
        }
        all_rankings['NET'] = net_rankings

    # Process each game
    processed_games = []
    unmatched_teams = []

    print("\n" + "=" * 60)
    print("PROCESSING SCHEDULE")
    print("=" * 60)

    for game in michigan_schedule:
        opponent = game['opponent']
        location = game['location']
        result = game['result']

        # Find rankings in all systems
        rankings_found = {}
        for system_name, rankings_dict in all_rankings.items():
            rank = find_net_rank(opponent, rankings_dict)
            if rank:
                rankings_found[system_name] = rank

        # Calculate average ranking (only from systems where team is ranked)
        if rankings_found:
            avg_rank = sum(rankings_found.values()) / len(rankings_found)
        else:
            avg_rank = None

        # Use NET rank for quadrant calculation (official NCAA metric)
        net_rank = rankings_found.get('NET', None)

        if net_rank:
            quadrant = determine_quadrant(net_rank, location)
        else:
            quadrant = 'Unknown'
            unmatched_teams.append(opponent)
            print(f"⚠️  Could not find NET rank for: {opponent}")

        processed_games.append({
            'date': game['date'],
            'opponent': opponent,
            'location': location,
            'result': result,
            'score': game['score'],
            'net_rank': net_rank if net_rank else 'N/A',
            'ap_rank': rankings_found.get('AP', 'NR'),
            'coaches_rank': rankings_found.get('Coaches', 'NR'),
            'kenpom_rank': rankings_found.get('KenPom', 'NR'),
            'torvik_rank': rankings_found.get('Torvik', 'NR'),
            'evanmiya_rank': rankings_found.get('EvanMiya', 'NR'),
            'avg_rank': round(avg_rank, 1) if avg_rank else 'N/A',
            'quadrant': quadrant
        })

    if unmatched_teams:
        print(f"\n⚠️  Total unmatched teams in NET: {len(unmatched_teams)}")
        print("Available teams in NET rankings (sample):")
        for i, team in enumerate(list(net_rankings.keys())[:20]):
            print(f"  - {team} (#{net_rankings[team]})")
        print("  ...")

    # Calculate average NET by quadrant for WINS only
    quadrant_stats = {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []}
    quadrant_avg_stats = {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []}

    # Also break down by location
    location_stats = {
        'Q1': {'Home': [], 'Away': [], 'Neutral': []},
        'Q2': {'Home': [], 'Away': [], 'Neutral': []},
        'Q3': {'Home': [], 'Away': [], 'Neutral': []},
        'Q4': {'Home': [], 'Away': [], 'Neutral': []}
    }

    for game in processed_games:
        if game['result'] == 'W':
            quadrant = game['quadrant']
            location = game['location']

            # NET rank stats
            if game['net_rank'] != 'N/A' and quadrant in quadrant_stats:
                quadrant_stats[quadrant].append(game['net_rank'])
                if quadrant in location_stats and location in location_stats[quadrant]:
                    location_stats[quadrant][location].append(game['net_rank'])

            # Average rank stats (composite across all systems)
            if game['avg_rank'] != 'N/A' and quadrant in quadrant_avg_stats:
                quadrant_avg_stats[quadrant].append(game['avg_rank'])

    # Print results
    print("\n" + "=" * 60)
    print("MICHIGAN WOLVERINES - RESUME ANALYSIS")
    print("=" * 60)

    print("\nQUADRANT WINS SUMMARY (NET Rankings):")
    print("-" * 60)

    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        wins = quadrant_stats[quad]
        if wins:
            avg_net = sum(wins) / len(wins)
            median_net = sorted(wins)[len(wins) // 2]
            print(f"\n{quad}: {len(wins)} wins | Avg NET: {avg_net:.1f} | Median NET: {median_net}")
            print(f"     NET ranks of wins: {sorted(wins)}")

            # Breakdown by location
            for loc in ['Home', 'Away', 'Neutral']:
                loc_wins = location_stats[quad][loc]
                if loc_wins:
                    loc_avg = sum(loc_wins) / len(loc_wins)
                    loc_median = sorted(loc_wins)[len(loc_wins) // 2]
                    print(f"     {loc}: {len(loc_wins)} wins | Avg: {loc_avg:.1f} | Median: {loc_median} | Ranks: {sorted(loc_wins)}")
        else:
            print(f"\n{quad}: 0 wins")

    print("\n" + "=" * 60)
    print("COMPOSITE RANKING AVERAGES BY QUADRANT:")
    print("(Average across NET, AP, Coaches, KenPom, Torvik, EvanMiya)")
    print("-" * 60)

    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        avg_wins = quadrant_avg_stats[quad]
        if avg_wins:
            avg_composite = sum(avg_wins) / len(avg_wins)
            median_composite = sorted(avg_wins)[len(avg_wins) // 2]
            print(f"\n{quad}: {len(avg_wins)} wins | Avg Composite Rank: {avg_composite:.1f} | Median: {median_composite:.1f}")
        else:
            print(f"\n{quad}: 0 wins")

    # Save to CSV with all rankings
    csv_filename = 'michigan_schedule_analysis.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['date', 'opponent', 'location', 'result', 'score',
                     'net_rank', 'ap_rank', 'coaches_rank', 'kenpom_rank',
                     'torvik_rank', 'evanmiya_rank', 'avg_rank', 'quadrant']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for game in processed_games:
            writer.writerow(game)

    print(f"\n✓ Full schedule with all rankings saved to {csv_filename}")

    # Save summary to separate CSV
    summary_filename = 'michigan_quadrant_summary.csv'
    with open(summary_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Quadrant', 'Wins', 'Average_NET', 'Median_NET', 'NET_Ranks'])

        for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
            wins = quadrant_stats[quad]
            if wins:
                avg_net = sum(wins) / len(wins)
                median_net = sorted(wins)[len(wins) // 2]
                writer.writerow([quad, len(wins), f"{avg_net:.1f}", median_net, sorted(wins)])
            else:
                writer.writerow([quad, 0, 'N/A', 'N/A', '[]'])

    print(f"✓ Quadrant summary saved to {summary_filename}")

    # Save location breakdown to separate CSV
    location_filename = 'michigan_location_breakdown.csv'
    with open(location_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Quadrant', 'Location', 'Wins', 'Average_NET', 'Median_NET', 'NET_Ranks'])

        for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
            for loc in ['Home', 'Away', 'Neutral']:
                loc_wins = location_stats[quad][loc]
                if loc_wins:
                    loc_avg = sum(loc_wins) / len(loc_wins)
                    loc_median = sorted(loc_wins)[len(loc_wins) // 2]
                    writer.writerow([quad, loc, len(loc_wins), f"{loc_avg:.1f}", loc_median, sorted(loc_wins)])

    print(f"✓ Location breakdown saved to {location_filename}")

    # Save Michigan's own rankings across all systems
    michigan_team_name = 'Michigan'
    michigan_own_rankings = {}
    for system_name, rankings_dict in all_rankings.items():
        rank = find_net_rank(michigan_team_name, rankings_dict)
        michigan_own_rankings[system_name] = rank if rank else 'NR'

    # Calculate Michigan's average ranking
    ranked_values = [v for v in michigan_own_rankings.values() if v != 'NR']
    if ranked_values:
        michigan_avg = sum(ranked_values) / len(ranked_values)
    else:
        michigan_avg = 'N/A'

    michigan_rankings_filename = 'michigan_own_rankings.csv'
    with open(michigan_rankings_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['System', 'Rank'])
        for system, rank in michigan_own_rankings.items():
            writer.writerow([system, rank])
        writer.writerow(['Average', round(michigan_avg, 1) if michigan_avg != 'N/A' else 'N/A'])

    print(f"✓ Michigan's rankings saved to {michigan_rankings_filename}")

    print("\n" + "=" * 60)
    print("MICHIGAN'S RANKINGS ACROSS SYSTEMS:")
    print("-" * 60)
    for system, rank in michigan_own_rankings.items():
        print(f"{system}: #{rank}" if rank != 'NR' else f"{system}: Not Ranked")
    if michigan_avg != 'N/A':
        print(f"\nComposite Average: #{michigan_avg:.1f}")

    return processed_games, quadrant_stats, location_stats

if __name__ == "__main__":
    analyze_schedule()
