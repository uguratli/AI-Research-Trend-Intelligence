# AI Research Trend Analysis

Discovering emerging AI research topics from arXiv using NLP and topic modeling.

## Project Overview

This project analyzes trends in AI research using arXiv papers and topic modeling.

By combining NLP, topic modeling, and time-series analysis, the project identifies:

• Emerging research topics  
• Declining research areas  
• High-impact topics  
• Long-term vs short-term research trends  

An interactive Streamlit dashboard allows users to explore topic trends over time.

## Dashboard Preview


Eklenecek

## Dataset

Source: arXiv API

Categories analyzed:
- cs.AI (Artificial Intelligence)
- cs.CL (Computational Linguistics)

Time range:
2021 — Present

Total papers analyzed:
~XX,XXX


## Methodology

The project pipeline consists of the following steps:

### 1. Data Collection
Papers were collected using the arXiv API, including titles, abstracts, publication dates, and URLs.

### 2. Text Embedding
Paper abstracts were converted into semantic embeddings using Sentence Transformers.

### 3. Topic Modeling
BERTopic was used to discover research topics from the corpus.

### 4. Topic Reduction
Topics were reduced to improve interpretability and remove redundant clusters.

### 5. Trend Analysis
Topic prevalence was tracked over time to compute:

• Growth (trend slope)  
• Acceleration (change in growth)  
• Topic volume (paper count)

### 6. Interactive Dashboard
An interactive Streamlit dashboard was built to explore trends and topic details.

## Example Visualizations


eklenecek

## Running the Dashboard

Install dependencies:

pip install -r requirements.txt

Run the Streamlit app:

streamlit run app.py
## Repository Structure

├── app.py                  # Streamlit dashboard
├── notebooks/              # Analysis notebooks
├── data/
│   ├── raw/
│   └── processed/
├── images/                 # Dashboard screenshots
├── src/                    # Utility scripts
└── README.md

## Tech Stack

Python  
Pandas  
BERTopic  
Sentence Transformers  
Scikit-learn  
Plotly  
Streamlit
## Future Improvements

• Add citation-based impact analysis  
• Integrate additional research sources  
• Improve topic labeling with LLMs  
• Deploy dashboard publicly
