import requests
import csv
import json
from datetime import datetime, timedelta

NEWS_API_URL = "https://newsapi.org/v2/everything"

MOVIE_KEYWORDS = ["film", "movie", "horror", "director", "actor", "box office", "trailer"]

def fetch_news(api_key, query, from_date, to_date, page=1):
    params = {
        "apiKey": api_key,
        "q": query,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "pageSize": 100,
        "page": page
    }

    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching news articles: {response.status_code}")

    return response.json().get("articles", [])


def extract_movie_keywords(articles):
    extracted_keywords = set()
    for article in articles:
        content = (article.get("title", "") + " " + article.get("description", "")).lower()
        for word in MOVIE_KEYWORDS:
            if word in content:
                extracted_keywords.add(word)
    return extracted_keywords


def snowball_sampling(api_key, seed_keywords, max_iterations=3, max_articles=500):
    all_articles = []
    new_keywords = set(seed_keywords)
    explored_keywords = set()

    # Define date range
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    iteration = 0

    while new_keywords and iteration < max_iterations and len(all_articles) < max_articles:
        current_keyword = new_keywords.pop()
        explored_keywords.add(current_keyword)

        print(f"Iteration {iteration + 1}: Fetching articles for '{current_keyword}'")

        # Fetch articles for the current keyword
        articles = fetch_news(api_key, current_keyword, from_date, to_date)
        all_articles.extend(articles)

        # Extract new movie-related keywords
        extracted_keywords = extract_movie_keywords(articles)
        new_keywords.update(extracted_keywords - explored_keywords)

        # Optionally allow manual keyword addition
        print(f"Suggested new keywords: {extracted_keywords}")
        manual_keywords = input("Enter additional keywords for the next iteration (comma-separated): ")
        if manual_keywords.strip():
            new_keywords.update(manual_keywords.strip().split(","))

        iteration += 1
        print(f"Collected {len(articles)} articles in this iteration.")

    # Limit total articles
    return all_articles[:max_articles]

def json_to_tsv(json_file, tsv_file):
    """
    Convert articles from a JSON file to a TSV file.

    Parameters:
    - json_file (str): Path to the input JSON file.
    - tsv_file (str): Path to the output TSV file.
    """
    with open(json_file, "r", encoding="utf-8") as infile:
        articles = json.load(infile)  # Load articles from JSON

    with open(tsv_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        # Write header
        writer.writerow(["Title", "Author", "Published At", "Source", "URL"])

        # Write article rows
        for article in articles:
            writer.writerow([
                article.get("title", ""),
                article.get("author", ""),
                article.get("publishedAt", ""),
                article.get("source", {}).get("name", ""),
                article.get("url", "")
            ])
    print(f"Articles have been saved to {tsv_file}")



# Example usage
if __name__ == "__main__":
    API_KEY = "fef5181e75ea4ee7a86fdb055f3f300b"
    SEED_KEYWORDS = ["Movie"]

    sampled_articles = snowball_sampling(API_KEY, SEED_KEYWORDS, max_iterations=5, max_articles=200)
    print(f"Collected {len(sampled_articles)} total articles.")

    # Save to JSON
    with open("snowball_sampled_articles.json", "w") as file:
        json.dump(sampled_articles, file, indent=4)
    print("Sampled articles saved to 'snowball_sampled_articles.json'")
    
    json_to_tsv("snowball_sampled_articles.json", "collected_articles.tsv")
