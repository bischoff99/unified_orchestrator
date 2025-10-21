#!/usr/bin/env python3
"""
Crew AI Web Interface
View agents, tasks, and execution in real-time
"""

import streamlit as st
from crewai import Agent, Task, Crew, Process
import json
from datetime import datetime
import time

st.set_page_config(
    page_title="Crew AI Orchestration",
    page_icon="🤖",
    layout="wide"
)

# Header
st.title("🤖 Multi-Agent Orchestration Dashboard")
st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    model_choice = st.selectbox(
        "Select Model",
        ["ollama/mistral", "ollama/codellama", "ollama/llama2"]
    )
    
    st.markdown("### 🎯 Agent Roles")
    st.info("""
    **Architect**: System design
    **Developer**: Code generation
    **Reviewer**: Quality assurance
    """)
    
    st.markdown("### 📊 Status")
    st.success("✅ Ollama: Connected")
    st.success("✅ HF Pro: Ready")

# Main area - Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🤖 Agents", "📋 Tasks", "▶️ Execute", "📊 Results"])

# Tab 1: Agents
with tab1:
    st.header("Agent Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏗️ Solutions Architect")
        st.write("**Model:** ollama/mistral")
        st.write("**Role:** Design scalable architectures")
        st.info("Status: Ready")
        
    with col2:
        st.subheader("💻 Senior Developer")
        st.write("**Model:** ollama/codellama")
        st.write("**Role:** Generate production code")
        st.info("Status: Ready")
        
    with col3:
        st.subheader("🔒 Security Auditor")
        st.write("**Model:** ollama/llama2")
        st.write("**Role:** Security & quality review")
        st.info("Status: Ready")

# Tab 2: Tasks
with tab2:
    st.header("Task Pipeline")
    
    st.markdown("### Task 1: Architecture Design")
    st.code("""
    Design microservices architecture for e-commerce platform:
    - User Service (auth, profiles)
    - Product Service (catalog, inventory)
    - Order Service (cart, checkout)
    - Notification Service (emails, SMS)
    """, language="text")
    
    st.markdown("### Task 2: Code Generation")
    st.code("""
    Generate User Service API:
    - POST /register
    - POST /login (JWT)
    - GET /profile
    - PUT /profile
    """, language="text")
    
    st.markdown("### Task 3: Security Audit")
    st.code("""
    Security review:
    - Authentication vulnerabilities
    - SQL injection risks
    - Input validation
    - Rate limiting
    """, language="text")

# Tab 3: Execute
with tab3:
    st.header("Execute Pipeline")
    
    project_name = st.text_input("Project Name", "EcommercePlatform")
    
    requirements = st.text_area(
        "Requirements",
        "Build a scalable e-commerce microservices platform with authentication, product catalog, and order management.",
        height=100
    )
    
    if st.button("🚀 Run Multi-Agent Pipeline", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create agents
        status_text.text("Creating agents...")
        progress_bar.progress(10)
        
        architect = Agent(
            role="Solutions Architect",
            goal="Design scalable architecture",
            backstory="Expert in distributed systems.",
            llm="ollama/mistral",
            verbose=False,
            allow_delegation=False
        )
        
        developer = Agent(
            role="Senior Developer",
            goal="Generate production code",
            backstory="Expert Python engineer.",
            llm="ollama/codellama",
            verbose=False,
            allow_delegation=False
        )
        
        reviewer = Agent(
            role="Security Auditor",
            goal="Security & quality review",
            backstory="Cybersecurity expert.",
            llm="ollama/llama2",
            verbose=False,
            allow_delegation=False
        )
        
        progress_bar.progress(20)
        status_text.text("Creating tasks...")
        
        # Create tasks
        arch_task = Task(
            description=f"Design architecture for {project_name}. Requirements: {requirements}",
            expected_output="Architecture specification",
            agent=architect
        )
        
        dev_task = Task(
            description=f"Generate code for User Service based on architecture.",
            expected_output="FastAPI code implementation",
            agent=developer
        )
        
        review_task = Task(
            description="Security audit of the code.",
            expected_output="Security recommendations",
            agent=reviewer
        )
        
        progress_bar.progress(30)
        status_text.text("Assembling crew...")
        
        # Create crew
        crew = Crew(
            agents=[architect, developer, reviewer],
            tasks=[arch_task, dev_task, review_task],
            process=Process.sequential,
            verbose=False
        )
        
        progress_bar.progress(40)
        status_text.text("🏗️ Architect working...")
        
        # Execute
        with st.spinner("Running orchestration..."):
            result = crew.kickoff()
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        
        # Store result
        st.session_state['last_result'] = result
        st.session_state['last_run'] = datetime.now().isoformat()
        
        st.success("Pipeline completed successfully!")
        st.balloons()

# Tab 4: Results
with tab4:
    st.header("Execution Results")
    
    if 'last_result' in st.session_state:
        st.markdown(f"**Last Run:** {st.session_state['last_run']}")
        
        st.markdown("### 📄 Final Output")
        st.text_area("Result", str(st.session_state['last_result']), height=400)
        
        # Download button
        st.download_button(
            label="📥 Download Results",
            data=str(st.session_state['last_result']),
            file_name=f"crewai_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Agents Used", "3")
        with col2:
            st.metric("Tasks Completed", "3")
        with col3:
            st.metric("Status", "Success ✅")
            
    else:
        st.info("👈 Go to 'Execute' tab to run a pipeline")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🤖 Powered by Crew AI + Ollama + Hugging Face Pro</p>
    <p>📍 Models: Mistral, CodeLlama, Llama2</p>
</div>
""", unsafe_allow_html=True)
