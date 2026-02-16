#!/usr/bin/env python3
"""
Main build script for NCAA NET Analyzer
Generates complete static site: home page + all team dashboards
"""

import sys
import shutil
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generators.home_page_generator import generate_home_page
from generators.dashboard_generator import generate_team_dashboard
from generators.comparison_page_generator import generate_comparison_page
from utils.team_config import load_teams


def clean_output_dir(output_dir='public'):
    """Remove and recreate output directory"""
    output_path = Path(output_dir)

    if output_path.exists():
        print(f"🗑️  Cleaning {output_dir}/...")
        shutil.rmtree(output_path)

    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / 'teams').mkdir(exist_ok=True)

    print(f"✅ Output directory ready: {output_dir}/\n")


def build():
    """Main build function"""
    print("=" * 60)
    print("🏀 NCAA NET Analyzer - Build Script")
    print("=" * 60)
    print()

    # Clean output directory
    clean_output_dir()

    # Load team configuration
    print("⚙️  Loading team configuration...")
    teams = load_teams()
    active_teams = [t for t in teams if t.get('active', True)]
    print(f"   Found {len(active_teams)} active teams\n")

    # Generate home page
    print("🏠 Generating home page...")
    try:
        generate_home_page()
        print()
    except Exception as e:
        print(f"❌ Failed to generate home page: {e}\n")
        return False

    # Generate comparison page
    print("⚔️  Generating comparison page...")
    try:
        generate_comparison_page()
        print()
    except Exception as e:
        print(f"❌ Failed to generate comparison page: {e}\n")
        return False

    # Generate team dashboards
    print(f"📊 Generating {len(active_teams)} team dashboards...")
    print("-" * 60)

    successful = 0
    failed = []

    for team in active_teams:
        team_name = team['name']
        team_slug = team['slug']

        try:
            success = generate_team_dashboard(team_slug)
            if success:
                print(f"  ✅ {team_name}")
                successful += 1
            else:
                print(f"  ⚠️  {team_name} (no data)")
                failed.append(team_name)
        except Exception as e:
            print(f"  ❌ {team_name}: {e}")
            failed.append(team_name)

    print("-" * 60)
    print()

    # Print summary
    print("=" * 60)
    print("📊 Build Summary")
    print("=" * 60)
    print(f"✅ Home page: Generated")
    print(f"✅ Comparison page: Generated")
    print(f"✅ Team dashboards: {successful}/{len(active_teams)}")

    if failed:
        print(f"⚠️  Failed: {len(failed)} teams")
        for team in failed:
            print(f"   - {team}")
    else:
        print("🎉 All teams generated successfully!")

    print()
    print(f"📁 Output directory: public/")
    print(f"   - public/index.html (home page)")
    print(f"   - public/compare/ (team comparison)")
    print(f"   - public/teams/{{team}}/ ({successful} teams)")
    print()

    # Test command
    print("🚀 To view locally, run:")
    print("   python3 -m http.server 8000 --directory public")
    print("   Then visit: http://localhost:8000")
    print()
    print("=" * 60)

    return len(failed) == 0


if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
