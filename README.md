# SLP Vehicle Defect Intelligence

An interactive Streamlit application for analyzing NHTSA vehicle complaint data using AI-powered insights.

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)
- OpenAI API key

## Installation & Setup

### 1. Install `uv`

Follow the official installation guide:

https://docs.astral.sh/uv/getting-started/installation/#installation-methods

### 2. Clone the Repository

```bash
git clone https://github.com/rzagni/slp-vehicle-defect-intelligence.git
cd slp-vehicle-defect-intelligence
```

### 3. Create Virtual Environment & Install Dependencies

```bash
uv sync
```

This creates a `.venv` directory and installs dependencies.

### 4. Activate the Virtual Environment

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

## Data Setup

### 5. Download NHTSA Complaint Database

Download the dataset:

https://static.nhtsa.gov/odi/ffdd/cmpl/FLAT_CMPL.zip

1. Extract the ZIP file.
2. Copy the extracted file(s) into the `db/` folder located in the project root:

```
slp-vehicle-defect-intelligence/
│
├── db/
│   └── <NHTSA files here>
```

### 6. Convert NHTSA Data to Parquet Format

From the project root directory:

```bash
python convert_to_parquet.py
```

This converts the complaint database into optimized Parquet format.

## Configure Environment Variables

Create a `.env` file in the project root directory:

```
slp-vehicle-defect-intelligence/.env
```

Add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Run the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

The app will open in your browser (typically at `http://localhost:8501`).

## Project Structure

```
slp-vehicle-defect-intelligence/
│
├── app.py
├── analysis.py
├── nhtsa_client.py
├── analysis.py
├── convert_to_parquet.py
├── uv.lock
├── db/
├── .env
├── .venv/
└── README.md
```

## Troubleshooting

- Ensure the NHTSA dataset is properly extracted before running the conversion script.
- Confirm your `.env` file contains a valid `OPENAI_API_KEY`.
- Make sure your virtual environment is activated before running the app.

---


# Architecture, Tradeoffs & Future Enhancements

## Overview

This prototype was built to help attorneys rapidly assess vehicle defect patterns, complaint severity, recall history, and similar case signals using publicly available NHTSA data. The design prioritizes functional completeness and clarity within an 8-hour MVP constraint while maintaining a clear path to production scalability. 

## Data Storage Strategy

For the MVP, the NHTSA complaints flat file was converted into a local **Parquet dataset** and loaded using Streamlit caching.

**Why Parquet:**
- Columnar format improves filtering performance
- Faster load times than raw text
- Smaller memory footprint than CSV
- Simple local deployment without infrastructure

The dataset is loaded once and filtered dynamically by make/model/year during vehicle analysis.

### Tradeoff

This approach is efficient for local prototyping but not ideal for production-scale usage. Since the dataset is loaded into memory, it assumes a single-user environment and limited concurrency.

In a production system, this would be replaced with:

- PostgreSQL for structured filtering
- Indexed queries for performance
- Cloud-hosted storage for scalability

## Semantic Search Architecture

Semantic search is implemented using OpenAI embeddings (`text-embedding-3-small`) and cosine similarity.

### Current Design

- Complaint summaries are embedded when a vehicle is analyzed
- Embeddings are cached per vehicle session
- Semantic similarity is computed in-memory using NumPy

This allows attorneys to search complaints by symptom description (e.g., “transmission slipping at highway speed”).

### Tradeoff

Embeddings are not persisted and are regenerated per vehicle session. This approach is appropriate for an MVP but would not scale to high traffic or cross-vehicle analysis.

### Production Upgrade Path

A scalable version would:

- Precompute embeddings
- Store them in a vector database (e.g., pgvector, Pinecone, FAISS)
- Enable indexed semantic search across all vehicles
- Reduce API calls and latency

## Case Strength Scoring

The MVP includes a configurable heuristic-based case strength score derived from:

- Number of injuries
- Crashes
- Fires
- Deaths
- Total complaint volume

Example structure:

```python
case_strength_score =
    (weight_injuries × injuries) +
    (weight_crashes × crashes) +
    (weight_fires × fires) +
    (weight_deaths × deaths) +
    (weight_volume × total_complaints)
