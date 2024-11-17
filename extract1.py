import requests
import csv

url = 'https://newsapi.org/v2/everything'
api_key = 'ec259888eb8c48399c83097c7e9fe21b'

# List of queries to fetch different sets of articles since we can't request more than 100 articles with free plan. 
queries = [
    'Substance movie demi',
    'Substance movie demi horror',
    'Substance demi',
    'Substance movie Coralie Fargeat',
    'Substance demi movie review'
]

# File to save the results(hard coded)
output_file = 'articles_output2.tsv'


# Write the output in tsv format
with open(output_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['Title', 'Author', 'Published At', 'Source', 'URL'])

    total_articles = 0

    # Fetch articles for each query
    for query in queries:
        params = {
            'q': query,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': 100,  # Max articles per query
            'apiKey': api_key
        }

        # Fetch the each page (only up to 100 articles per query btw since it's limited to the plan)
        response = requests.get(url, params=params)
        print(f"Fetching articles for query: {query}")

        if response.status_code == 200:
            articles = response.json().get('articles', [])
            if not articles:
                print(f"No articles found for query: {query}")
                continue

            for article in articles:
                writer.writerow([
                    article.get('title', 'N/A'),
                    article.get('author', 'N/A'),
                    article.get('publishedAt', 'N/A'),
                    article.get('source', {}).get('name', 'N/A'),
                    article.get('url', 'N/A')
                ])
                total_articles += 1
                print(f"Saved article {total_articles}: {article.get('title', 'N/A')}")
        else:
            print(f"Error fetching articles for query {query}: {response.status_code} - {response.json().get('message', '')}")

print(f"Total articles saved: {total_articles}")
