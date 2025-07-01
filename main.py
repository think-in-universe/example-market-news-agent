import time
import datetime
import json
import requests
import os
from google import genai
from google.genai.types import (
    Tool,
    GenerateContentConfig,
    GoogleSearch,
    HarmCategory,
    HarmBlockThreshold,
)
from google.genai import types

# Get key from env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
model_name = "gemini-2.5-flash-preview-05-20"

safety_settings = [
    types.SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
]

google_search_tool = Tool(google_search=GoogleSearch())


def run_llm_inference(
    prompt: str, system_prompt: str = "You are a helpful AI assistant."
) -> str:
    """
    LLM call.
    """
    # print(f"   System Prompt: {system_prompt}")
    # print(f"   User Prompt: {prompt[:250]}...")
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.5,
            safety_settings=safety_settings,
        ),
    )
    # print(
    #     f"   LLM Response: {response.text[:250]}..."
    # )  # Print a snippet of the response
    return response.text if response.text is not None else ""


def run_llm_inference_with_grounding(
    prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
) -> str:
    """
    LLM call that uses grounding sources.
    """
    # print(f"   System Prompt: {system_prompt}")
    # print(f"   User Prompt: {prompt[:250]}...")

    google_search_tool = Tool(google_search=GoogleSearch())

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[google_search_tool],
            temperature=0.5,
            safety_settings=safety_settings,
        ),
    )
    # print(
    #     f"   LLM Response: {response.text[:250]}..."
    # )  # Print a snippet of the response
    return response.text if response.text is not None else ""


def parse_json(json_output: str):
    # Parsing out the markdown fencing
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(
                lines[i + 1 :]
            )  # Remove everything before "```json"
            json_output = json_output.split("```")[
                0
            ]  # Remove everything after the closing "```"
            break  # Exit the loop once "```json" is found
    return json_output


def get_companies(target_query: str) -> list:
    """
    LLM call to get a list of companies (name and ticker) based on a target query.
    """
    system_prompt = "You are an AI assistant specializing in financial markets. Given a market, sector, or theme, identify key publicly traded companies or currencies or cryptocurrencies or bonds within it. Return a JSON list of objects, where each object has 'name' and 'ticker'."
    response = run_llm_inference(
        prompt=f"market/theme: {target_query}",
        system_prompt=system_prompt,
    )

    try:
        response = parse_json(response)
        companies = json.loads(response)
        if isinstance(companies, list):
            return [
                {
                    "name": comp.get("name", "Unknown"),
                    "ticker": comp.get("ticker", "N/A"),
                }
                for comp in companies
                if isinstance(comp, dict) and "name" in comp and "ticker" in comp
            ]
        else:
            print("Warning: LLM response was not a valid JSON list.")
            return []
    except json.JSONDecodeError:
        print("Error: Could not decode LLM response as JSON.")
        return []


class SentimentAnalysisAgent:
    def __init__(self):
        self.target_query = os.getenv(
            "TARGET_QUERY"
        )  # User's initial query (e.g., "US Semiconductor Market")
        self.tracked_companies = (
            []
        )  # List of dicts: [{'name': 'Nvidia', 'ticker': 'NVDA', 'news_sources': [], 'facts': [], 'recommendations': []}, ...]
        self.facts_history_limit_per_company = 30  # Max facts per company

    def get_target_query_and_companies(self):
        """Identifies companies based on the target query from environment variable."""
        if not self.target_query:
            print("Error: TARGET_QUERY environment variable not set.")
            print(
                "Please set the TARGET_QUERY environment variable (e.g., export TARGET_QUERY='US Semiconductor Market') and rerun the agent."
            )
            return False

        print(f"\n🔍 Identifying companies for target query: '{self.target_query}'...")
        companies_found = get_companies(self.target_query)

        if not companies_found:
            print(
                "Could not identify any companies for the given query. Please try a different query."
            )
            return False

        for comp_info in companies_found:
            if "name" in comp_info and "ticker" in comp_info:
                self.tracked_companies.append(
                    {
                        "name": comp_info["name"],
                        "ticker": comp_info["ticker"].upper(),
                        "facts": [],  # List of fact objects for this company
                        "recommendations": [],  # List of recommendation strings for this company
                    }
                )
            else:
                print(
                    f"Warning: Found company data missing name or ticker: {comp_info}"
                )

        if not self.tracked_companies:
            print("No valid companies to track. Exiting.")
            return False

        print("\n📈 Agent will track the following companies:")
        for company_data in self.tracked_companies:
            print(f"   - {company_data['name']} ({company_data['ticker']})")
        return True

    def fetch_news_for_company(self, company_data: dict) -> list:
        """Fetches news for a specific company."""
        company_name = company_data["name"]
        print(f"\n📰 Fetching news for {company_name}...")
        system_prompt = (
            "You are a financial news aggregator AI. Fetch recent top news articles about the company "
            f"{company_name}. Return a JSON list of objects with 'summary', 'relevance_score', 'sentiment_score' and 'original_news_title'."
        )
        raw_news_items = []
        news_summary = run_llm_inference_with_grounding(
            f"Fetch recent top news about {company_name}.", system_prompt
        )
        try:
            news_summary = parse_json(news_summary)
            raw_news_items = json.loads(news_summary)
            if not isinstance(raw_news_items, list):
                print(
                    f"Warning: LLM response for {company_name} was not a valid JSON list."
                )
                return []
            for news_item in raw_news_items:
                print(
                    f"   - {news_item.get('summary', 'No summary provided')} (Relevance: {news_item.get('relevance_score', 'N/A')}, Sentiment: {news_item.get('sentiment_score', 'N/A')})"
                )
        except json.JSONDecodeError:
            print(
                f"Error: Could not decode news summary for {company_name} as JSON. Response was: {news_summary}"
            )
            return []
        print(f"   Fetched {len(raw_news_items)} raw news items for {company_name}.")
        return raw_news_items

    def update_and_prune_facts_for_company(self, new_facts: list, company_data: dict):
        """Merges new facts and prunes old ones for a specific company."""
        company_name = company_data["name"]
        print(f"\n🔄 Updating and pruning facts for {company_name}...")
        system_prompt = (
            "You are a financial data manager AI. Given a list of old facts and new facts, create a single list of relevant facts for a company. "
            "Ensure no duplicates based on 'summary' content. Return a JSON list of objects with 'summary', 'relevance_score', 'sentiment_score' and 'original_news_title'."
        )
        old_facts = company_data["facts"]

        prompt = (
            f"Company: {company_name}\n\n"
            f"Old Facts:\n{json.dumps(old_facts, indent=2)}\n\n"
            f"New Facts:\n{json.dumps(new_facts, indent=2)}\n\n"
            "Merge these into a single list of unique facts, ensuring no duplicates based on 'fact' content. "
            "Return the merged list as a JSON array."
        )

        try:
            response_json = run_llm_inference(prompt, system_prompt)
            response_json = parse_json(response_json)
            merged_facts = json.loads(response_json)

            if not isinstance(merged_facts, list):
                print(
                    f"Warning: Merged facts for {company_name} were not returned as a valid JSON list."
                )
                return

            company_data["facts"] = merged_facts
            print(
                f"   Updated facts for {company_name}. Total facts now: {len(company_data['facts'])}"
            )
        except json.JSONDecodeError:
            print(
                f"Error: Could not decode merged facts for {company_name} as JSON. Response was: {response_json}"
            )
        except Exception as e:
            print(f"Unexpected error updating facts for {company_name}: {e}")
            import traceback

            traceback.print_exc()

    def generate_recommendations_for_company(self, company_data: dict):
        """Generates recommendations for a specific company."""
        company_name = company_data["name"]
        company_ticker = company_data["ticker"]
        print(
            f"\n💡 Generating recommendations for {company_name} ({company_ticker})..."
        )

        if not company_data["facts"]:
            print(
                f"   No facts available for {company_name} to generate recommendations."
            )
            company_data["recommendations"] = [
                f"{company_ticker} (Neutral): No specific recommendation due to lack of fresh data for {company_name}."
            ]
            return

        facts_summary = "\n".join([f"{f}" for f in company_data["facts"]])

        prompt = (
            f"Based on the following recent facts for company {company_name} (company ticker {company_ticker}), "
            f"provide an investment recommendation. Format: "
            f"'{company_ticker.upper()} (Sentiment: Long/Short/Neutral): Justification. Hypothetical 1: ... Hypothetical 2: ...'. "
            f"Consider overall sentiment, key events, and potential future impacts.\n\nFacts:\n{facts_summary}"
        )
        system_prompt = (
            "You are a senior investment analyst AI. Provide clear, concise, actionable investment "
            "recommendations with justifications and two distinct hypothetical scenarios based on provided facts."
        )

        recommendation_text = run_llm_inference(prompt, system_prompt)
        company_data["recommendations"] = [recommendation_text]

    def run_hourly_cycle(self):
        """Runs the agent's core logic for all tracked companies."""
        print(
            f"\n--- Starting new hourly cycle for query '{self.target_query}' at {datetime.datetime.now()} ---"
        )

        for company_data in self.tracked_companies:
            company_name = company_data["name"]
            company_ticker = company_data["ticker"]
            print(f"\n--- Processing Company: {company_name} ({company_ticker}) ---")

            new_facts = self.fetch_news_for_company(company_data)
            self.update_and_prune_facts_for_company(new_facts, company_data)
            self.generate_recommendations_for_company(company_data)

        print("\n--- Hourly Cycle Summary: Recommendations ---")
        for company_data in self.tracked_companies:
            print(
                f"\nRecommendations for {company_data['name']} ({company_data['ticker']}):"
            )
            if company_data["recommendations"]:
                for rec in company_data["recommendations"]:
                    print(f"  {rec}")
            else:
                print("  No recommendations generated.")
        print("-------------------------------------------")
        print(f"--- Cycle complete. Next run in approximately 1 hour. ---")

    def start(self):
        """Starts the agent and runs its main loop."""
        if not self.get_target_query_and_companies():
            print("Agent initialization failed. Exiting.")
            return

        try:
            while True:
                self.run_hourly_cycle()
                wait_time_seconds = 3600
                # wait_time_seconds = 45 # For quick testing
                print(f"\nSleeping for {wait_time_seconds // 60} minutes...")
                time.sleep(wait_time_seconds)
        except KeyboardInterrupt:
            print("\nAgent stopped by user. Exiting.")
        except Exception as e:
            print(f"\nAn unexpected error occurred in the main loop: {e}")
            import traceback

            traceback.print_exc()
        finally:
            print("Agent shutting down.")


if __name__ == "__main__":
    agent = SentimentAnalysisAgent()
    agent.start()
