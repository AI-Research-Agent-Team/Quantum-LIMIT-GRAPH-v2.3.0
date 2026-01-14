import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Quantum Limit Orchestrator", layout="wide")

st.title("⚛️ Quantum-LIMIT Agent Command Center")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Benchmark Control")
    num_nodes = st.slider("Graph Nodes", 10, 1000, 50)
    workers = st.slider("Parallel Workers", 1, 16, 4)
    
    if st.button("Run Local Benchmark"):
        with st.spinner("Crunching Quantum Graphs..."):
            # Call our own API to simulate an agent task
            payload = {"task_id": "manual_test", "graph_parameters": {"nodes": num_nodes}}
            res = requests.post("http://api:8000/agent/tasks", json=payload).json()
            st.success("Optimization Complete!")
            st.json(res)

with col2:
    st.subheader("Live Leaderboard Stats")
    # Mock data - connect this to a real database later
    df = pd.DataFrame({
        "Agent": ["Our_Agent", "Baseline_GPT4", "Random_Search"],
        "Accuracy": [0.98, 0.85, 0.42],
        "Latency (ms)": [120, 450, 10]
    })
    st.dataframe(df)
    st.bar_chart(df.set_index("Agent"))
