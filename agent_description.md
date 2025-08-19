### Trading News Agent

The Trading News Agent is an AI-powered system designed to continuously monitor financial markets, perform sentiment analysis on news, and generate hourly investment recommendations. It identifies relevant companies based on a user-defined market, sector, or theme, fetches real-time news, extracts key facts, and provides actionable insights.

#### Key Features
*   **Dynamic Company Identification**: Automatically identifies publicly traded companies, currencies, or cryptocurrencies relevant to a specified market, sector, or theme.
*   **Hourly News Aggregation**: Fetches recent and top news articles for all tracked entities using Google Search for grounding.
*   **Fact Management & Analysis**: Processes news to extract key facts, assesses their relevance and sentiment, and maintains a curated list of up-to-date information for each company.
*   **Investment Recommendation Generation**: Produces clear, concise investment recommendations (Long/Short/Neutral) with justifications and hypothetical scenarios based on the aggregated financial facts.
*   **Continuous Monitoring**: Operates in a continuous loop, updating news and recommendations approximately every hour.

#### Inputs
*   **Environment Variable**: `GEMINI_API_KEY` (Your Google Gemini API key for AI model access).
*   **Environment Variable**: `TARGET_QUERY` (The specific market, sector, or theme to track, e.g., "US Semiconductor Market", "Cryptocurrency", "European Banking Sector").

#### Outputs
*   **Standard Output (stdout)**:
    *   Logs detailing the agent's progress, including company identification, news fetching, and fact updates.
    *   Hourly investment recommendations for each tracked company, including sentiment, justification, and hypothetical scenarios.