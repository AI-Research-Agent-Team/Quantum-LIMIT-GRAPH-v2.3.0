"""
Quantum LIMIT-GRAPH Dashboard
Interactive Streamlit dashboard for leaderboards, evaluations, and analytics
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Any

# Page configuration
st.set_page_config(
    page_title="Quantum LIMIT-GRAPH Dashboard",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .agent-card {
        border: 2px solid #1f77b4;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-good { color: #17a2b8; font-weight: bold; }
    .score-fair { color: #ffc107; font-weight: bold; }
    .score-poor { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8080")

# Cache configuration
@st.cache_data(ttl=60)
def fetch_leaderboard(metric: str = "overall_score", time_range: str = "all_time") -> Dict:
    """Fetch leaderboard data from API"""
    try:
        response = requests.get(
            f"{API_URL}/api/v1/leaderboard/",
            params={"metric": metric, "time_range": time_range, "limit": 100}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching leaderboard: {e}")
        return {"rankings": []}

@st.cache_data(ttl=300)
def fetch_stats() -> Dict:
    """Fetch leaderboard statistics"""
    try:
        response = requests.get(f"{API_URL}/api/v1/leaderboard/stats")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return {}

@st.cache_data(ttl=120)
def fetch_agent_trends(agent_id: str, metric: str = "overall_score", days: int = 30) -> Dict:
    """Fetch agent performance trends"""
    try:
        response = requests.get(
            f"{API_URL}/api/v1/leaderboard/trends/{agent_id}",
            params={"metric": metric, "days": days}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching trends: {e}")
        return {"trends": []}

def get_score_class(score: float) -> str:
    """Get CSS class for score"""
    if score >= 0.8:
        return "score-excellent"
    elif score >= 0.7:
        return "score-good"
    elif score >= 0.6:
        return "score-fair"
    else:
        return "score-poor"

def format_score(score: float) -> str:
    """Format score with color coding"""
    css_class = get_score_class(score)
    return f'<span class="{css_class}">{score:.3f}</span>'

# ============================================================================
# Sidebar
# ============================================================================

st.sidebar.image("https://via.placeholder.com/200x80?text=Quantum+LIMIT", use_container_width=True)
st.sidebar.title("⚛️ Navigation")

page = st.sidebar.radio(
    "Select Page",
    ["🏆 Leaderboard", "📊 Analytics", "🔍 Agent Details", "📈 Trends", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

# Time range filter
time_range_options = {
    "Last 24 Hours": "last_day",
    "Last Week": "last_week",
    "Last Month": "last_month",
    "Last Year": "last_year",
    "All Time": "all_time"
}
time_range_label = st.sidebar.selectbox(
    "Time Range",
    list(time_range_options.keys()),
    index=4
)
time_range = time_range_options[time_range_label]

# Metric filter
metric_options = {
    "Overall Score": "overall_score",
    "Parsing Accuracy": "parsing_accuracy",
    "Semantic Coherence": "semantic_coherence",
    "Hallucination Avoidance": "hallucination_avoidance",
    "Latency Performance": "latency_score",
    "Quantum Performance": "quantum_performance"
}
metric_label = st.sidebar.selectbox(
    "Ranking Metric",
    list(metric_options.keys()),
    index=0
)
metric = metric_options[metric_label]

# Language filter
language = st.sidebar.selectbox(
    "Language Filter",
    ["All Languages", "English (en)", "Spanish (es)", "Chinese (zh)", 
     "Japanese (ja)", "Korean (ko)", "Arabic (ar)", "French (fr)"]
)
lang_code = language.split("(")[1].rstrip(")") if "(" in language else None

# Auto-refresh
auto_refresh = st.sidebar.checkbox("Auto Refresh (60s)", value=False)
if auto_refresh:
    import time
    time.sleep(60)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("""
**Quantum LIMIT-GRAPH v2.3.0**

Multilingual Quantum Research Agent Benchmark

[Documentation](https://github.com/AI-Research-Agent-Team/Quantum-LIMIT-GRAPH-v2.3.0) | 
[API Docs](http://localhost:8080/docs)
""")

# ============================================================================
# Main Content
# ============================================================================

if page == "🏆 Leaderboard":
    st.markdown('<h1 class="main-header">🏆 Agent Leaderboard</h1>', unsafe_allow_html=True)
    
    # Fetch data
    leaderboard_data = fetch_leaderboard(metric, time_range)
    stats = fetch_stats()
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Agents",
            stats.get("total_agents", 0),
            help="Total number of registered agents"
        )
    
    with col2:
        st.metric(
            "Total Evaluations",
            stats.get("total_evaluations", 0),
            help="Total benchmark runs completed"
        )
    
    with col3:
        st.metric(
            "Active (30d)",
            stats.get("active_agents_30d", 0),
            help="Agents with evaluations in last 30 days"
        )
    
    with col4:
        avg_score = stats.get("average_overall_score", 0.0)
        st.metric(
            "Average Score",
            f"{avg_score:.3f}",
            help="Average overall score across all agents"
        )
    
    st.markdown("---")
    
    # Leaderboard table
    st.subheader(f"Rankings by {metric_label}")
    
    if leaderboard_data.get("rankings"):
        rankings = leaderboard_data["rankings"]
        
        # Create DataFrame
        df = pd.DataFrame([
            {
                "Rank": r.get("rank", 0),
                "Agent": r.get("agent_name", r.get("agent_id", "Unknown")),
                "Score": r.get("score", 0.0),
                "Tests": r.get("total_evaluations", 0),
                "Last Active": r.get("last_evaluation", "Never")[:10],
                "Trend": "📈" if r.get("rank_change", 0) > 0 else "📉" if r.get("rank_change", 0) < 0 else "➡️"
            }
            for r in rankings[:50]  # Top 50
        ])
        
        # Style the dataframe
        def color_score(val):
            if val >= 0.8:
                return 'background-color: #d4edda'
            elif val >= 0.7:
                return 'background-color: #d1ecf1'
            elif val >= 0.6:
                return 'background-color: #fff3cd'
            else:
                return 'background-color: #f8d7da'
        
        styled_df = df.style.applymap(color_score, subset=['Score'])
        st.dataframe(styled_df, use_container_width=True, height=600)
        
        # Top 3 podium
        st.markdown("### 🥇 Top 3 Agents")
        top3_cols = st.columns(3)
        
        medals = ["🥇", "🥈", "🥉"]
        colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
        
        for idx, (col, medal, color) in enumerate(zip(top3_cols, medals, colors)):
            if idx < len(rankings):
                agent = rankings[idx]
                with col:
                    st.markdown(f"""
                    <div class="agent-card" style="border-color: {color}">
                        <h2 style="text-align: center;">{medal}</h2>
                        <h3 style="text-align: center;">{agent.get('agent_name', 'Unknown')}</h3>
                        <p style="text-align: center; font-size: 2rem; font-weight: bold; color: {color};">
                            {agent.get('score', 0.0):.3f}
                        </p>
                        <p style="text-align: center;">
                            {agent.get('total_evaluations', 0)} evaluations
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No leaderboard data available")

elif page == "📊 Analytics":
    st.markdown('<h1 class="main-header">📊 Performance Analytics</h1>', unsafe_allow_html=True)
    
    leaderboard_data = fetch_leaderboard("overall_score", time_range)
    
    if leaderboard_data.get("rankings"):
        rankings = leaderboard_data["rankings"]
        
        # Score distribution
        st.subheader("Score Distribution")
        scores = [r.get("score", 0.0) for r in rankings]
        
        fig_hist = px.histogram(
            x=scores,
            nbins=20,
            labels={"x": "Overall Score", "y": "Number of Agents"},
            title="Distribution of Agent Scores",
            color_discrete_sequence=["#1f77b4"]
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Metric comparison
        st.subheader("Multi-Metric Comparison (Top 10)")
        
        top10 = rankings[:10]
        metrics_data = {
            "Agent": [r.get("agent_name", r.get("agent_id", "Unknown")) for r in top10],
            "Parsing": [r.get("parsing_accuracy", 0.0) for r in top10],
            "Coherence": [r.get("semantic_coherence", 0.0) for r in top10],
            "Hallucination": [r.get("hallucination_avoidance", 0.0) for r in top10],
            "Latency": [r.get("latency_score", 0.0) for r in top10],
            "Quantum": [r.get("quantum_performance", 0.0) for r in top10]
        }
        
        fig_radar = go.Figure()
        
        for i, agent in enumerate(metrics_data["Agent"][:5]):  # Top 5 for clarity
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    metrics_data["Parsing"][i],
                    metrics_data["Coherence"][i],
                    metrics_data["Hallucination"][i],
                    metrics_data["Latency"][i],
                    metrics_data["Quantum"][i]
                ],
                theta=["Parsing", "Coherence", "Hallucination", "Latency", "Quantum"],
                fill='toself',
                name=agent
            ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title="Top 5 Agents - Metric Comparison"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)

elif page == "🔍 Agent Details":
    st.markdown('<h1 class="main-header">🔍 Agent Performance Details</h1>', unsafe_allow_html=True)
    
    leaderboard_data = fetch_leaderboard("overall_score", "all_time")
    
    if leaderboard_data.get("rankings"):
        # Agent selector
        agent_options = {
            r.get("agent_name", r.get("agent_id", "Unknown")): r.get("agent_id")
            for r in leaderboard_data["rankings"]
        }
        
        selected_agent_name = st.selectbox(
            "Select Agent",
            list(agent_options.keys())
        )
        
        selected_agent_id = agent_options[selected_agent_name]
        
        # Find agent data
        agent_data = next(
            (r for r in leaderboard_data["rankings"] if r.get("agent_id") == selected_agent_id),
            None
        )
        
        if agent_data:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"### {selected_agent_name}")
                st.markdown(f"**Rank:** #{agent_data.get('rank', 'N/A')}")
                st.markdown(f"**Overall Score:** {agent_data.get('score', 0.0):.3f}")
                st.markdown(f"**Total Evaluations:** {agent_data.get('total_evaluations', 0)}")
                st.markdown(f"**Last Active:** {agent_data.get('last_evaluation', 'Never')[:10]}")
            
            with col2:
                # Component scores
                scores_df = pd.DataFrame({
                    "Metric": [
                        "Parsing Accuracy",
                        "Semantic Coherence",
                        "Hallucination Avoidance",
                        "Latency Performance",
                        "Quantum Performance"
                    ],
                    "Score": [
                        agent_data.get("parsing_accuracy", 0.0),
                        agent_data.get("semantic_coherence", 0.0),
                        agent_data.get("hallucination_avoidance", 0.0),
                        agent_data.get("latency_score", 0.0),
                        agent_data.get("quantum_performance", 0.0)
                    ]
                })
                
                fig_bar = px.bar(
                    scores_df,
                    x="Score",
                    y="Metric",
                    orientation='h',
                    title="Component Scores",
                    color="Score",
                    color_continuous_scale="RdYlGn",
                    range_color=[0, 1]
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

elif page == "📈 Trends":
    st.markdown('<h1 class="main-header">📈 Performance Trends</h1>', unsafe_allow_html=True)
    
    st.info("Select an agent to view historical performance trends")
    
    # Implementation for trends visualization
    st.markdown("Coming soon: Historical performance tracking and trend analysis")

elif page == "⚙️ Settings":
    st.markdown('<h1 class="main-header">⚙️ Dashboard Settings</h1>', unsafe_allow_html=True)
    
    st.subheader("API Configuration")
    st.text_input("API URL", value=API_URL, disabled=True)
    
    st.subheader("Display Preferences")
    st.checkbox("Dark Mode", value=False)
    st.slider("Refresh Interval (seconds)", 30, 300, 60)
    
    st.subheader("Export Options")
    if st.button("Export Leaderboard Data (CSV)"):
        leaderboard_data = fetch_leaderboard("overall_score", "all_time")
        if leaderboard_data.get("rankings"):
            df = pd.DataFrame(leaderboard_data["rankings"])
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "leaderboard.csv",
                "text/csv"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    Quantum LIMIT-GRAPH Dashboard v2.3.0 | 
    <a href="https://github.com/AI-Research-Agent-Team/Quantum-LIMIT-GRAPH-v2.3.0">GitHub</a> | 
    <a href="/docs">API Docs</a>
</div>
""", unsafe_allow_html=True)
