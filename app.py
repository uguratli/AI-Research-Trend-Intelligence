import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import json

@st.cache_data
def load_data():
    topics_df = pd.read_csv("topics_trend_analysis.csv", index_col=0)
    trend_share = pd.read_csv("trend_share.csv", index_col=0)
    impact_df = pd.read_csv("top10_impact_topics.csv", index_col=0)
    representative_docs_df = pd.read_csv("representative_docs.csv")

    with open('topic_words.json', 'r') as file:
        topic_words = json.load(file)

    return topics_df, trend_share, impact_df, representative_docs_df, topic_words

topics_df, trend_share, impact_df, representative_docs_df, topic_words = load_data()



with open('topic_words.json', 'r') as file:
    topic_words = json.load(file)


st.set_page_config(
    page_title="AI Research Trend Intelligence",
    layout="wide"
)

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <h1 style='text-align: center;'>AI Research Trend Intelligence Dashboard</h1>
    <h1 style='text-align: center;'>Tracking Emerging Topics in arXiv (2018–2024)</h1>
    <p style='text-align: center; color: gray;'>
    Multi-window growth analysis of AI research topics using NLP and regression-based trend metrics.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------
# KPI ROW
# -----------------------------
col1, col2, col3, col4 = st.columns(4)
total_docs = topics_df['Count'].sum()

total_topics = topics_df['label'].nunique()

growing_topics = (topics_df["slope_12m"] > 0).sum()
growing_pct = 100 * growing_topics / total_topics

accelerating_topics = (
    (topics_df["slope_12m"] > 0) &
    (topics_df["acceleration"] > 0)
).sum()
accelerating_pct = 100 * accelerating_topics / total_topics

col1.metric("Documents", f"{total_docs:,}")
col2.metric("Topics", total_topics)
col3.metric("Growing Topics (%)", f"{growing_pct:.1f}%")
col4.metric("Accelerating Topics (%)", f"{accelerating_pct:.1f}%")

st.markdown("---")


# -----------------------------
# GROWTH VS ACCELERATION QUADRANT
# -----------------------------
fig_growth_acc = px.scatter(
    topics_df,
    y="slope_12m",
    x="acceleration",
    size="scaled_acc",
    color="category",
    hover_name="label",
    hover_data={
        "Count": True,
        "slope_12m": ':.4f',
        "acceleration": ':.4f'
    },
    template="plotly_white"
)

fig_growth_acc.add_vline(x=0, line_dash="dash")
fig_growth_acc.add_hline(y=0, line_dash="dash")

fig_growth_acc.update_layout(
    title="Trend Momentum Map",
    xaxis_title="Acceleration",
    yaxis_title="Growth (12-month slope)",
    height=550
)

# -----------------------------
# GROWTH VS VOLUME QUADRANT
# -----------------------------

fig_growth_volume = px.scatter(
    topics_df,
    y="slope_12m",
    x="Count",
    size="scaled_acc",
    color="category",
    hover_name="label",
    hover_data={
        "Count": True,
        "slope_12m": ':.4f',
        "acceleration": ':.4f'
    },
    template="plotly_white"
)

fig_growth_volume.update_layout(
    title="Trend Strength vs Topic Size",
    xaxis_title="Topic Volume (Number of Papers)",
    yaxis_title="Growth (12-month slope)",
    height=550
)
fig_growth_volume.add_vline(x=0, line_dash="dash")
fig_growth_volume.add_hline(y=0, line_dash="dash")

st.subheader("Trend Intelligence Maps")

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_growth_acc, use_container_width=True)
    st.caption(
        """
        **Growth vs Acceleration**

        Topics in the **upper-right quadrant** represent rapidly growing research directions 
        with increasing momentum. These are strong candidates for emerging trends in AI research.
        """
    )

with col2:
    st.plotly_chart(fig_growth_volume, use_container_width=True)
    st.caption(
        """
        **Growth vs Volume**

        Topics in the **upper-right area** combine large research activity with strong growth.  
        Topics in the **upper-left area** may represent smaller but emerging research directions.
        """
    )
st.markdown("---")

# -----------------------------
# MAIN QUADRANT
# -----------------------------
st.subheader("Trend Consistency Map")

fig_trend_consistency = px.scatter(
    topics_df,
    x="slope_24m",
    y="slope_12m",
    size="scaled_growth_size",
    color="category",
    hover_data={
        "scaled_growth_size": False,
        "scaled_acc": False,
        "Count": True,
        "slope_12m": ':.4f',
        "acceleration": ':.4f'
    },
    template="plotly_white"
)

fig_trend_consistency.add_vline(x=0, line_dash="dash")
fig_trend_consistency.add_hline(y=0, line_dash="dash")
fig_trend_consistency.update_traces(marker=dict(opacity=0.8))
fig_trend_consistency.update_layout(
    title="Short-Term vs Long-Term Trend",
    xaxis_title="Long-Term Growth (24-month slope)",
    yaxis_title="Short-Term Growth (12-month slope)",
    height=550
)
st.plotly_chart(fig_trend_consistency, use_container_width=True)

st.caption(
"""
**Short-Term vs Long-Term Trend**

This plot compares short-term and long-term growth signals for each research topic.

- **Upper-right quadrant** → consistently growing topics over both time horizons  
- **Upper-left quadrant** → recently accelerating topics (new emerging signals)  
- **Lower-right quadrant** → mature topics that may be losing momentum  
- **Lower-left quadrant** → declining research areas
"""
)

st.markdown("---")

# -----------------------------
# TOP GROWING TABLE
# -----------------------------
st.subheader("Top Growing Emerging Topics")

st.dataframe(topics_df.sort_values("slope_12m", ascending=False).head(10)[["Count", "label", "slope_12m", "category"]], use_container_width=True)

st.markdown("---")

# -----------------------------
# TOP IMPACT TABLE
# -----------------------------
st.subheader("Top Impactful Emerging Topics")

st.dataframe(
    impact_df.sort_values("growth_score", ascending=False).head(10)[[
        "label",
        "slope_12m",
        "acceleration",
        "Count",
        "growth_score"
    ]],
    use_container_width=True
)

st.markdown("---")

# -----------------------------
# DRILLDOWN
# -----------------------------
st.subheader("Deep Dive")

selected_labels = st.multiselect(
    "Select Topics",
    topics_df["label"])
if selected_labels:
    selected_topic_ids = topics_df[topics_df["label"].isin(selected_labels)].index.values
    fig_topic_timeseries = go.Figure()

    for label, topic_id in zip(selected_labels, selected_topic_ids):

        fig_topic_timeseries.add_trace(
            go.Scatter(
                x=trend_share.index,
                y=trend_share[str(topic_id)]/ trend_share[str(topic_id)].max() + 0.0000001,
                mode="lines",
                name=label
            )
        )

    fig_topic_timeseries.update_layout(
        template="plotly_white",
        title=f"Trend Over Time — {selected_labels}",
        xaxis_title="Date",
        yaxis_title="Topic Share",
        hovermode="x unified"
    )
    st.plotly_chart(fig_topic_timeseries, use_container_width=True)


    for label, topic_id in zip(selected_labels, selected_topic_ids):

        topic_words_df = pd.DataFrame({'word': topic_words[str(topic_id)][0], 'score': topic_words[str(topic_id)][1]}, columns=["word", "score"])


        doc_count = topics_df.loc[topic_id, "Count"]
        st.markdown(f"## {label} (Documents: {doc_count})")
        fig_keywords = px.bar(
            topic_words_df,
            x="score",
            y="word",
            orientation="h",
            title=f"Top Keywords — {label}"
        )

        fig_keywords.update_layout(
            template="plotly_white",
            yaxis=dict(autorange="reversed")
        )

        st.plotly_chart(fig_keywords, use_container_width=True)

        st.markdown("### Representative Papers")
        topic_papers = representative_docs_df[representative_docs_df["topic_id"] == topic_id].sort_values("rank").head(5)
        for _, row in topic_papers.iterrows():
            st.markdown(f"**{row['title']}**")
            st.markdown(f"*Published: {row['published']}*")
            st.markdown(f"{row['abstract'][:300]}...")
            st.markdown(f"[Read More]({row['paper_id']})")
            st.divider()



else:
    st.info("Please select at least one topic.")
