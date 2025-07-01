# Trading News Agent

This project implements an AI-powered trading news agent that continuously monitors financial news, performs sentiment analysis, and generates investment recommendations for a specified market, sector, or theme. The agent identifies relevant companies, fetches their news, extracts key facts, and provides hourly investment recommendations.

## Features

- **Dynamic Company Identification**: Automatically identifies publicly traded companies, currencies, or cryptocurrencies based on a user-defined target query (e.g., "US Semiconductor Market").
- **Hourly News Fetching**: Periodically fetches recent news articles for all tracked companies using Google Search.
- **Sentiment Analysis**: Analyzes news articles to determine relevance and sentiment scores.
- **Fact Management**: Merges new facts from news with existing knowledge, ensuring uniqueness and pruning old information.
- **Investment Recommendations**: Generates actionable investment recommendations (Long/Short/Neutral) with justifications and hypothetical scenarios based on aggregated facts.
- **Modular Design**: Utilizes Google's Gemini API for LLM interactions and grounding with Google Search.

## Setup

To set up and run the Trading News Agent, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/trading-news-agent.git
    cd trading-news-agent
    ```

2.  **Install dependencies**:
    This project uses `uv` for package management. If you don't have `uv` installed, you can install it via `pip`:
    ```bash
    pip install uv
    ```
    Then, install the project dependencies:
    ```bash
    uv sync
    ```

3.  **Set up Environment Variables**:
    You need to set your Google Gemini API key and the target query. Create a `.env` file in the root directory or set them directly in your shell:

    ```bash
    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    export TARGET_QUERY="US Semiconductor Market" # Example: "US Semiconductor Market", "Cryptocurrency", "European Banking Sector"
    ```
    Replace `"YOUR_GEMINI_API_KEY"` with your actual API key obtained from Google AI Studio.

## Usage

To start the agent, run the `main.py` script:

```bash
uv run main.py
```

The agent will start identifying companies, fetching news, and generating recommendations hourly. You will see output in your console detailing its progress and the generated recommendations.

To stop the agent, press `Ctrl+C` in the terminal.

## Environment Variables

-   `GEMINI_API_KEY`: Your Google Gemini API key. **Required**.
-   `TARGET_QUERY`: The market, sector, or theme you want the agent to track (e.g., "US Semiconductor Market"). **Required**.

