#!/usr/bin/env python3
"""
🚀 CrewAI Development Team CLI
Command-line interface for multi-agent development orchestration

Usage:
  python crewai_cli.py feature --name "API Gateway" --priority high --complexity medium
  python crewai_cli.py bug --id "BUG-2024-789" --severity critical --component "auth"
  python crewai_cli.py review --pr "PR-456" --files 12 --lines 300
  python crewai_cli.py status
  python crewai_cli.py agents
"""

import argparse
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Import the development orchestrator
from launch_dev_team import DevelopmentOrchestrator, log_with_timestamp

class CrewAICLI:
    """Command-line interface for CrewAI development team"""
    
    def __init__(self):
        self.orchestrator = DevelopmentOrchestrator()
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the development team"""
        print("🤖 Initializing CrewAI Development Team...")
        self.orchestrator.initialize_dev_team()
        self.orchestrator.setup_communication_channels()
        self.orchestrator.configure_dev_workflows()
        print("✅ System ready!\n")
    
    def run_feature_development(self, args):
        """Execute feature development mission"""
        print("🆕 FEATURE DEVELOPMENT MISSION")
        print("=" * 50)
        
        project_data = {
            "feature_name": args.name,
            "priority": args.priority,
            "complexity": args.complexity,
            "estimated_effort": getattr(args, 'effort', '3 days'),
            "requirements": getattr(args, 'requirements', [])
        }
        
        result = self.orchestrator.execute_development_mission("feature_development", project_data)
        self._display_mission_results(result)
    
    def run_bug_fix(self, args):
        """Execute bug fix mission"""
        print("🐛 BUG FIX MISSION")
        print("=" * 50)
        
        project_data = {
            "bug_id": args.id,
            "severity": args.severity,
            "component": args.component,
            "reported_by": getattr(args, 'reporter', 'User'),
            "description": getattr(args, 'description', 'Bug needs investigation')
        }
        
        result = self.orchestrator.execute_development_mission("bug_fix", project_data)
        self._display_mission_results(result)
    
    def run_code_review(self, args):
        """Execute code review mission"""
        print("👀 CODE REVIEW MISSION")
        print("=" * 50)
        
        project_data = {
            "pull_request": args.pr,
            "lines_changed": args.lines,
            "files_modified": args.files,
            "author": getattr(args, 'author', 'Developer'),
            "branch": getattr(args, 'branch', 'feature-branch')
        }
        
        result = self.orchestrator.execute_development_mission("code_review", project_data)
        self._display_mission_results(result)
    
    def show_status(self):
        """Display system status"""
        print("📊 CREWAI SYSTEM STATUS")
        print("=" * 50)
        
        # Agent status
        print("🤖 ACTIVE AGENTS:")
        for agent_id, agent in self.orchestrator.agents.items():
            print(f"   {agent.name}: {agent.performance_score:.1f}% - {agent.status}")
        
        print()
        
        # Communication channels
        print("📡 COMMUNICATION CHANNELS:")
        for channel, config in self.orchestrator.communication_channels.items():
            participants = len(config['participants'])
            print(f"   {channel.replace('_', ' ').title()}: {participants} agents - {config['status']}")
        
        print()
        
        # Workflows
        print("🔄 CONFIGURED WORKFLOWS:")
        for workflow, config in self.orchestrator.workflow_patterns.items():
            phases = len(config['phases'])
            print(f"   {workflow.replace('_', ' ').title()}: {phases} phases - {config['status']}")
        
        print()
        
        # Mission stats
        stats = self.orchestrator.mission_stats
        print("📈 MISSION STATISTICS:")
        print(f"   Projects Completed: {stats['projects_completed']}")
        print(f"   Features Delivered: {stats['features_delivered']}")
        print(f"   Bugs Fixed: {stats['bugs_fixed']}")
        print(f"   Code Quality Score: {stats['code_quality_score']:.1f}%")
    
    def show_agents(self):
        """Display detailed agent information"""
        print("🤖 DEVELOPMENT TEAM AGENTS")
        print("=" * 50)
        
        for agent_id, agent in self.orchestrator.agents.items():
            print(f"\n🔷 {agent.name} ({agent.id})")
            print(f"   Role: {agent.role}")
            print(f"   Specialization: {agent.specialization}")
            print(f"   Performance: {agent.performance_score:.1f}%")
            print(f"   Status: {agent.status}")
            print(f"   Skills: {', '.join(agent.skills)}")
            print(f"   Tools: {', '.join(agent.tools)}")
    
    def _display_mission_results(self, result: Dict[str, Any]):
        """Display mission execution results"""
        print(f"\n🎯 MISSION RESULTS")
        print(f"Mission ID: {result['mission_id']}")
        print(f"Type: {result['mission_type'].replace('_', ' ').title()}")
        print(f"Timestamp: {result['timestamp']}")
        
        print(f"\n📋 EXECUTION SUMMARY:")
        print(f"   Agents Involved: {len(result['agents_involved'])}")
        print(f"   Phases Completed: {len(result['phases_completed'])}")
        print(f"   Deliverables: {len(result['deliverables'])}")
        
        print(f"\n📊 PERFORMANCE METRICS:")
        for key, value in result['performance_metrics'].items():
            formatted_key = key.replace('_', ' ').title()
            print(f"   {formatted_key}: {value}")
        
        print(f"\n📝 PHASES EXECUTED:")
        for phase in result['phases_completed']:
            agents_str = ', '.join(phase['agents'])
            print(f"   {phase['phase']}: {phase['duration']} ({agents_str})")
        
        print(f"\n📦 DELIVERABLES:")
        for i, deliverable in enumerate(result['deliverables'], 1):
            print(f"   {i}. {deliverable}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")

def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="CrewAI Development Team CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python crewai_cli.py feature --name "User Dashboard" --priority high --complexity medium
  python crewai_cli.py bug --id "BUG-2024-123" --severity high --component "auth-service"
  python crewai_cli.py review --pr "PR-456" --files 8 --lines 245
  python crewai_cli.py status
  python crewai_cli.py agents
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Feature development command
    feature_parser = subparsers.add_parser('feature', help='Run feature development mission')
    feature_parser.add_argument('--name', required=True, help='Feature name')
    feature_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'critical'], 
                               default='medium', help='Priority level')
    feature_parser.add_argument('--complexity', choices=['low', 'medium', 'high'], 
                               default='medium', help='Complexity level')
    feature_parser.add_argument('--effort', help='Estimated effort (e.g., "3 days")')
    
    # Bug fix command
    bug_parser = subparsers.add_parser('bug', help='Run bug fix mission')
    bug_parser.add_argument('--id', required=True, help='Bug ID')
    bug_parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'],
                           default='medium', help='Bug severity')
    bug_parser.add_argument('--component', required=True, help='Affected component')
    bug_parser.add_argument('--reporter', help='Bug reporter')
    bug_parser.add_argument('--description', help='Bug description')
    
    # Code review command
    review_parser = subparsers.add_parser('review', help='Run code review mission')
    review_parser.add_argument('--pr', required=True, help='Pull request ID')
    review_parser.add_argument('--files', type=int, default=5, help='Number of files modified')
    review_parser.add_argument('--lines', type=int, default=150, help='Number of lines changed')
    review_parser.add_argument('--author', help='Code author')
    review_parser.add_argument('--branch', help='Source branch')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Agents command
    subparsers.add_parser('agents', help='Show detailed agent information')
    
    return parser

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 CrewAI Development Team CLI")
    print("=" * 50)
    
    try:
        cli = CrewAICLI()
        
        if args.command == 'feature':
            cli.run_feature_development(args)
        elif args.command == 'bug':
            cli.run_bug_fix(args)
        elif args.command == 'review':
            cli.run_code_review(args)
        elif args.command == 'status':
            cli.show_status()
        elif args.command == 'agents':
            cli.show_agents()
        
    except KeyboardInterrupt:
        print("\n❌ Mission aborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()