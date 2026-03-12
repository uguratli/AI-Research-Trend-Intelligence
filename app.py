import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
import json

topics_df = pd.read_csv("topics_trend_analysis.csv", index_col=0)
trend_share = pd.read_csv("trend_share.csv", index_col=0)
impact_df = pd.read_csv("top10_impact_topics.csv", index_col=0)
representative_docs_df = pd.read_csv("representative_docs.csv")


mn = MinMaxScaler()
topics_df[["scaled_acc", "scaled_growth_size"]] = mn.fit_transform(topics_df[["acceleration", "growth_size"]])
topics_df["scaled_acc"].fillna(0, inplace=True)
topics_df["scaled_growth_size"].fillna(0, inplace=True)
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
    <h1 style='text-align: center;'>Emerging AI Research Trends (arXiv 2018–2024)</h1>
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

total_topics = len(topics_df)
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
# MAIN QUADRANT
# -----------------------------
st.subheader("Trend Intelligence Map")

fig_quadrant = px.scatter(
    topics_df,
    x="slope_24m",
    y="slope_12m",
    size="scaled_growth_size",
    color="category",
    hover_name="label",
    template="plotly_white"
)

fig_quadrant.add_vline(x=0, line_dash="dash")
fig_quadrant.add_hline(y=0, line_dash="dash")


st.plotly_chart(fig_quadrant, use_container_width=True)

st.markdown(
    "<p style='color: gray;'>Topics in the upper-right quadrant show sustained and accelerating growth.</p>",
    unsafe_allow_html=True
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
# VOLUME VS GROWTH QUADRANT
# -----------------------------
st.subheader("Trend Intelligence Map")

fig_quadrant = px.scatter(
    topics_df,
    x="Count",
    y="slope_12m",
    size="scaled_acc",
    color="category",
    hover_name="label",
    template="plotly_white"
)

fig_quadrant.add_vline(x=0, line_dash="dash")
fig_quadrant.add_hline(y=0, line_dash="dash")


st.plotly_chart(fig_quadrant, use_container_width=True)

st.markdown(
    "<p style='color: gray;'>Topics in the upper-right quadrant show sustained and accelerating growth.</p>",
    unsafe_allow_html=True
)

st.markdown("---")
# -----------------------------
# DRILLDOWN
# -----------------------------
st.subheader("Topic Drilldown")

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
                y=trend_share[str(topic_id)]/ trend_share[str(topic_id)].max(),
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
    # burada topic'e göre filtreleyip time series fig üret
    st.plotly_chart(fig_topic_timeseries, use_container_width=True)


    for label, topic_id in zip(selected_labels, selected_topic_ids):

        topic_words_df = pd.DataFrame({'word': topic_words[str(topic_id)][0], 'score': topic_words[str(topic_id)][1]}, columns=["word", "score"])


        doc_count = topics_df.loc[topic_id, "Count"]
        st.markdown(f"### {label} (Documents: {doc_count})")
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

        st.markdown("#### Representative Papers")
        topic_papers = representative_docs_df[representative_docs_df["topic_id"] == topic_id].sort_values("rank").head(5)
        for _, row in topic_papers.iterrows():
            st.markdown(f"**{row['title']}**")
            st.markdown(f"*Published: {row['published']}*")
            st.markdown(f"{row['abstract'][:300]}...")
            st.markdown(f"[Read More]({row['paper_id']})")
            st.divider()



else:
    st.info("Please select at least one topic.")
