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

## License

Add your project license information here.



