#!/usr/bin/env python3
"""
MCP Generator - Main Entry Point

Generate complete MCP servers automatically using AI agent orchestration.

Usage:
    python generate.py --api stripe
    python generate.py --api github --verbose
    python generate.py --list
"""

import argparse
import sys
from pathlib import Path
from crew import create_mcp_generator_crew


# Supported APIs (can be extended)
SUPPORTED_APIS = {
    "stripe": "Payment processing and financial APIs",
    "github": "Code hosting and version control",
    "easyship": "Shipping and logistics",
    "openai": "AI and language models",
    "slack": "Team communication and collaboration",
    "discord": "Community chat and messaging",
    "twitter": "Social media and microblogging",
    "notion": "Workspace and notes",
    "airtable": "Database and spreadsheets",
    "shopify": "E-commerce platform"
}


def show_banner():
    """Display welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🤖  MCP SERVER GENERATOR  🤖                   ║
║                                                           ║
║     Automatic MCP Server Creation with AI Agents         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def list_supported_apis():
    """List all supported APIs"""
    print("\n📋 Supported APIs:")
    print("=" * 60)
    for api, description in SUPPORTED_APIS.items():
        print(f"  • {api:<15} - {description}")
    print("=" * 60)
    print("\nUsage: python generate.py --api <api_name>")
    print("Example: python generate.py --api stripe\n")


def validate_api(api_name: str) -> tuple[bool, str]:
    """
    Validate if API is supported
    
    Returns:
        (is_valid, message)
    """
    api_lower = api_name.lower()
    
    if api_lower in SUPPORTED_APIS:
        return True, f"✅ {api_name} is supported"
    else:
        return False, f"⚠️  {api_name} not in supported list (will attempt anyway)"


def generate_mcp_server(api_name: str, verbose: bool = True, output_dir: str = None, no_prompt: bool = False):
    """
    Generate MCP server for specified API
    
    Args:
        api_name: Name of the API
        verbose: Show detailed output
        output_dir: Output directory for generated files
    """
    show_banner()
    
    # Validate API
    is_valid, message = validate_api(api_name)
    print(message)
    
    if not is_valid:
        print("\n💡 Tip: Use --list to see supported APIs")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            return
    
    print(f"\n🎯 Target API: {api_name}")
    print(f"📁 Output: {output_dir or 'output/'}")
    print(f"🔊 Verbose: {verbose}")
    
    # Create output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path(__file__).parent / "output" / f"{api_name}-mcp-server"
    
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Output directory ready: {output_path}")
    
    # Create and run crew
    print("\n" + "=" * 60)
    print("🚀 Initializing AI Agent Crew...")
    print("=" * 60)
    
    crew = create_mcp_generator_crew(api_name, verbose=verbose)
    
    # Show crew info
    info = crew.get_crew_info()
    print(f"\n👥 Crew: {info['crew_name']}")
    print(f"🎯 Target: {info['api_target']}")
    print(f"📊 Process: {info['workflow']}")
    print("\n🤖 Active Agents:")
    for agent, role in info['agents'].items():
        print(f"   {agent.replace('_', ' ').title():<20} → {role}")
    
    print("\n📝 Workflow Phases:")
    for phase in info['phases']:
        print(f"   {phase}")
    
    # Generate
    print("\n" + "=" * 60)
    if not no_prompt:
        try:
            input("Press Enter to start generation (or Ctrl+C to cancel)...")
        except EOFError:
            pass  # Non-interactive mode
    print("=" * 60)
    
    result = crew.generate_mcp_server()
    
    # Display result
    print("\n" + "=" * 60)
    if result['success']:
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"\n{result['message']}")
        print(f"\n📦 Generated: {api_name}-mcp-server/")
        print(f"📂 Location: {output_path}")
        print("\n📚 Next Steps:")
        print("   1. Review generated code")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Configure API key in .env")
        print("   4. Test: python server.py demo")
        print("   5. Integrate with Claude Desktop")
    else:
        print("❌ GENERATION FAILED")
        print("=" * 60)
        print(f"\nError: {result.get('error', 'Unknown error')}")
        print("\n💡 Troubleshooting:")
        print("   - Check your internet connection")
        print("   - Verify API name spelling")
        print("   - Try again with --verbose for more details")
    
    print("\n" + "=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate MCP servers automatically using AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate.py --api stripe
  python generate.py --api github --verbose
  python generate.py --list
  python generate.py --api custom-api --output ./my-server

For more information, see README.md
        """
    )
    
    parser.add_argument(
        '--api',
        type=str,
        help='API name to generate MCP server for (e.g., stripe, github)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all supported APIs'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed agent reasoning and outputs'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory for generated files'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='MCP Generator v1.0.0'
    )
    
    parser.add_argument(
        '--no-prompt',
        action='store_true',
        help='Skip confirmation prompt and start immediately'
    )
    
    args = parser.parse_args()
    
    # Show banner
    if not args.list and not args.api:
        show_banner()
        parser.print_help()
        sys.exit(0)
    
    # List supported APIs
    if args.list:
        show_banner()
        list_supported_apis()
        sys.exit(0)
    
    # Generate MCP server
    if args.api:
        try:
            generate_mcp_server(
                api_name=args.api,
                verbose=args.verbose,
                output_dir=args.output,
                no_prompt=args.no_prompt
            )
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
