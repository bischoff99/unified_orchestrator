#!/usr/bin/osascript
-- Master Client Coordination Script
-- Orchestrates Cursor IDE, Claude Desktop, and Perplexity Desktop

on run argv
	if (count of argv) < 2 then
		return "Usage: osascript coordinate_clients.scpt <phase> <feature_description>"
	end if
	
	set workflowPhase to item 1 of argv
	set featureDescription to item 2 of argv
	
	coordinateWorkflow(featureDescription, workflowPhase)
end run

-- Main coordination handler
on coordinateWorkflow(feature_description, phase)
	log "Starting phase: " & phase
	
	if phase is "research" then
		performResearchPhase(feature_description)
		
	else if phase is "planning" then
		performPlanningPhase(feature_description)
		
	else if phase is "development" then
		performDevelopmentPhase(feature_description)
		
	else if phase is "testing" then
		performTestingPhase(feature_description)
		
	else if phase is "deployment" then
		performDeploymentPhase(feature_description)
		
	else if phase is "documentation" then
		performDocumentationPhase(feature_description)
		
	else
		return "Unknown phase: " & phase
	end if
	
	return "Phase " & phase & " completed successfully"
end coordinateWorkflow

-- PHASE 1: Research (Perplexity Desktop)
on performResearchPhase(feature_description)
	activatePerplexity()
	
	tell application "System Events"
		-- Create new research query
		keystroke "n" using command down
		delay 0.5
		
		-- Type research query
		keystroke "Research implementation patterns for: " & feature_description
		keystroke return
		delay 5
		
		-- Copy research results
		keystroke "a" using command down
		delay 0.5
		keystroke "c" using command down
		delay 0.5
		
		-- Save to file (via Terminal)
		my saveClipboardToFile("research_results.md")
		
		-- Create Linear epic
		keystroke "n" using command down
		delay 0.5
		keystroke "Create Linear epic for: " & feature_description
		keystroke return
		delay 3
		
		-- Create Notion page
		keystroke "n" using command down
		delay 0.5
		keystroke "Create Notion research page for: " & feature_description
		keystroke return
		delay 3
	end tell
	
	log "Research phase completed"
end performResearchPhase

-- PHASE 2: Planning (Claude Desktop + Perplexity)
on performPlanningPhase(feature_description)
	-- Start with Claude for analysis
	activateClaude()
	
	tell application "System Events"
		-- Create technical specification
		keystroke "Create technical specification for: " & feature_description
		keystroke return
		delay 3
		
		-- Use Desktop Commander to read research
		keystroke "Use desktop-commander to read research_results.md and create a detailed technical specification"
		keystroke return
		delay 5
		
		-- Copy spec
		keystroke "a" using command down
		delay 0.5
		keystroke "c" using command down
	end tell
	
	-- Switch to Perplexity for task creation
	activatePerplexity()
	
	tell application "System Events"
		-- Create Linear tasks
		keystroke "n" using command down
		delay 0.5
		keystroke "v" using command down -- Paste spec
		delay 0.5
		keystroke return
		keystroke "Create Linear sub-tasks for each component in this specification"
		keystroke return
		delay 5
	end tell
	
	log "Planning phase completed"
end performPlanningPhase

-- PHASE 3: Development (Cursor IDE)
on performDevelopmentPhase(feature_description)
	activateCursor()
	
	tell application "System Events"
		-- Open Agent Mode
		keystroke "l" using command down
		delay 1
		
		-- Switch to Agent mode
		keystroke tab
		delay 0.5
		keystroke "Agent"
		keystroke return
		delay 1
		
		-- Generate implementation
		keystroke "Read the specification from ChromaDB and generate complete implementation for: " & feature_description
		keystroke return
		delay 10
		
		-- Let Agent Mode work
		delay 20
		
		-- Save to Supermemory
		keystroke "l" using command down
		delay 1
		keystroke "Save implementation patterns to Supermemory"
		keystroke return
		delay 3
	end tell
	
	log "Development phase completed"
end performDevelopmentPhase

-- PHASE 4: Testing (All Clients)
on performTestingPhase(feature_description)
	-- Start with Cursor unit tests
	activateCursor()
	
	tell application "System Events"
		keystroke "l" using command down
		delay 1
		keystroke "Run all tests for " & feature_description
		keystroke return
		delay 10
	end tell
	
	-- Claude for browser testing
	activateClaude()
	
	tell application "System Events"
		keystroke "Use chrome-control to run E2E tests for " & feature_description
		keystroke return
		delay 10
	end tell
	
	-- Perplexity to check known issues
	activatePerplexity()
	
	tell application "System Events"
		keystroke "n" using command down
		delay 0.5
		keystroke "Check my Space for known issues with: " & feature_description
		keystroke return
		delay 5
		
		-- Update Linear with test results
		keystroke "Update Linear tasks with test results: all tests passing"
		keystroke return
		delay 3
	end tell
	
	log "Testing phase completed"
end performTestingPhase

-- PHASE 5: Deployment (Claude Coordinating)
on performDeploymentPhase(feature_description)
	activateClaude()
	
	tell application "System Events"
		-- Git operations via Desktop Commander
		keystroke "Use desktop-commander to commit and push: feat: " & feature_description
		keystroke return
		delay 5
	end tell
	
	-- Switch to Perplexity for PR
	activatePerplexity()
	
	tell application "System Events"
		keystroke "n" using command down
		delay 0.5
		keystroke "Create GitHub PR for feature: " & feature_description & " with Linear tasks linked"
		keystroke return
		delay 5
		
		-- Notify Slack
		keystroke "Send Slack notification to #deployments about: " & feature_description
		keystroke return
		delay 3
		
		-- Update Notion
		keystroke "Update Notion deployment checklist for: " & feature_description
		keystroke return
		delay 3
	end tell
	
	log "Deployment phase completed"
end performDeploymentPhase

-- PHASE 6: Documentation (All Clients)
on performDocumentationPhase(feature_description)
	-- Perplexity creates main docs
	activatePerplexity()
	
	tell application "System Events"
		keystroke "n" using command down
		delay 0.5
		keystroke "Create comprehensive Notion documentation for: " & feature_description
		keystroke return
		delay 10
		
		-- Update Space with learnings
		keystroke "Add implementation learnings to my Space for: " & feature_description
		keystroke return
		delay 5
	end tell
	
	-- Cursor generates code docs
	activateCursor()
	
	tell application "System Events"
		keystroke "l" using command down
		delay 1
		keystroke "Agent"
		keystroke return
		delay 1
		keystroke "Generate complete code documentation for " & feature_description
		keystroke return
		delay 10
	end tell
	
	-- Claude documents decisions
	activateClaude()
	
	tell application "System Events"
		keystroke "Use sequential-thinking to document all decisions made for: " & feature_description
		keystroke return
		delay 10
	end tell
	
	log "Documentation phase completed"
end performDocumentationPhase

-- Helper Functions
on activatePerplexity()
	tell application "Perplexity"
		activate
	end tell
	delay 1
end activatePerplexity

on activateClaude()
	tell application "Claude"
		activate
	end tell
	delay 1
end activateClaude

on activateCursor()
	tell application "Cursor"
		activate
	end tell
	delay 1
end activateCursor

on saveClipboardToFile(filename)
	tell application "Terminal"
		activate
		delay 0.5
	end tell
	
	tell application "System Events"
		keystroke "pbpaste > ~/Developer/projects/unified_orchestrator/" & filename
		keystroke return
		delay 1
	end tell
end saveClipboardToFile

-- Utility to check if app is running
on isAppRunning(appName)
	tell application "System Events"
		set appList to name of every process
		return (appName is in appList)
	end tell
end isAppRunning

-- Ensure all apps are ready
on ensureAppsReady()
	set requiredApps to {"Perplexity", "Claude", "Cursor"}
	
	repeat with appName in requiredApps
		if not isAppRunning(appName) then
			tell application appName
				activate
				delay 2
			end tell
		end if
	end repeat
	
	return true
end ensureAppsReady
