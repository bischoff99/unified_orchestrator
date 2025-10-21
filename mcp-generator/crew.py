"""
MCP Generator Crew
Coordinates multiple agents to generate complete MCP servers
"""

from crewai import Crew, Process
from agents import (
    create_api_researcher,
    create_mcp_architect,
    create_python_developer,
    create_qa_engineer,
    create_devops_configurator
)
from tasks import (
    create_research_task,
    create_architecture_task,
    create_development_task,
    create_testing_task,
    create_configuration_task
)


class MCPGeneratorCrew:
    """
    MCP Generator Crew
    
    Coordinates multiple specialized agents to automatically generate
    complete MCP server projects from API specifications.
    
    Workflow:
    1. Researcher → Analyzes API documentation
    2. Architect → Designs MCP server structure
    3. Developer → Writes production code
    4. QA Engineer → Tests implementation
    5. DevOps → Creates configuration & docs
    """
    
    def __init__(self, api_name: str, verbose: bool = True):
        """
        Initialize the MCP Generator Crew
        
        Args:
            api_name: Name of API to generate MCP server for (e.g., 'stripe', 'github')
            verbose: Whether to show detailed agent reasoning
        """
        self.api_name = api_name
        self.verbose = verbose
        
        # Create specialized agents
        self.researcher = create_api_researcher()
        self.architect = create_mcp_architect()
        self.developer = create_python_developer()
        self.qa_engineer = create_qa_engineer()
        self.devops = create_devops_configurator()
        
        print(f"🤖 MCP Generator Crew initialized for: {api_name}")
        print(f"👥 Agents ready: Researcher, Architect, Developer, QA, DevOps")
    
    def generate_mcp_server(self) -> dict:
        """
        Generate a complete MCP server using the agent crew.
        
        Returns:
            Dictionary with generation results and outputs
        """
        print(f"\n🚀 Starting MCP server generation for: {self.api_name}")
        print("=" * 60)
        
        # Create tasks
        tasks = [
            create_research_task(self.researcher, self.api_name),
            create_architecture_task(self.architect, self.api_name),
            create_development_task(self.developer, self.api_name),
            create_testing_task(self.qa_engineer, self.api_name),
            create_configuration_task(self.devops, self.api_name)
        ]
        
        # Create crew with sequential process
        crew = Crew(
            agents=[
                self.researcher,
                self.architect,
                self.developer,
                self.qa_engineer,
                self.devops
            ],
            tasks=tasks,
            process=Process.sequential,  # Tasks execute one after another
            verbose=self.verbose
        )
        
        # Execute the crew
        print("\n📋 Executing task workflow...")
        print("1️⃣  Research Phase - Analyzing API...")
        print("2️⃣  Architecture Phase - Designing MCP server...")
        print("3️⃣  Development Phase - Writing code...")
        print("4️⃣  Testing Phase - Validating quality...")
        print("5️⃣  Configuration Phase - Creating docs & config...")
        print()
        
        try:
            result = crew.kickoff()
            
            print("\n" + "=" * 60)
            print("✅ MCP Server Generation Complete!")
            print("=" * 60)
            
            return {
                "success": True,
                "api_name": self.api_name,
                "result": result,
                "message": f"Successfully generated {self.api_name} MCP server"
            }
            
        except Exception as e:
            print("\n" + "=" * 60)
            print(f"❌ Generation Failed: {str(e)}")
            print("=" * 60)
            
            return {
                "success": False,
                "api_name": self.api_name,
                "error": str(e),
                "message": f"Failed to generate {self.api_name} MCP server"
            }
    
    def get_crew_info(self) -> dict:
        """
        Get information about the crew and its capabilities.
        
        Returns:
            Dictionary with crew information
        """
        return {
            "crew_name": "MCP Generator Crew",
            "api_target": self.api_name,
            "agents": {
                "researcher": "Analyzes API documentation",
                "architect": "Designs MCP server structure",
                "developer": "Writes production code",
                "qa_engineer": "Tests and validates",
                "devops": "Creates configuration & docs"
            },
            "workflow": "Sequential",
            "phases": [
                "1. Research - API Analysis",
                "2. Architecture - Design",
                "3. Development - Implementation",
                "4. Testing - Validation",
                "5. Configuration - Setup"
            ]
        }


def create_mcp_generator_crew(api_name: str, verbose: bool = True) -> MCPGeneratorCrew:
    """
    Factory function to create an MCP Generator Crew.
    
    Args:
        api_name: Name of API to generate MCP server for
        verbose: Whether to show detailed agent reasoning
        
    Returns:
        Configured MCPGeneratorCrew instance
    """
    return MCPGeneratorCrew(api_name=api_name, verbose=verbose)


# Example usage
if __name__ == "__main__":
    # Example: Generate a Stripe MCP server
    crew = create_mcp_generator_crew("stripe", verbose=True)
    
    # Show crew info
    info = crew.get_crew_info()
    print(f"\n{info['crew_name']}")
    print(f"Target API: {info['api_target']}")
    print(f"Workflow: {info['workflow']}")
    print("\nAgents:")
    for agent, role in info['agents'].items():
        print(f"  - {agent.title()}: {role}")
    
    # Generate the MCP server
    result = crew.generate_mcp_server()
    
    if result['success']:
        print(f"\n✅ {result['message']}")
        print(f"\nGenerated files are ready!")
    else:
        print(f"\n❌ {result['message']}")
        print(f"Error: {result.get('error')}")
