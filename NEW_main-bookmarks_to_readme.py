import argparse
import html2text
import os
import requests
import tldextract
from bs4 import BeautifulSoup
from collections import defaultdict
from typing import List
from tqdm import tqdm
from urllib.parse import urlsplit

categories = {
    "AI": ["openai","artificial intelligence","machine learning","deep learning", "AI Research", "AI Products", "AI Education", "AI News", "AI Communities", "AI Ethics", "NLP", "Computer Vision", "Robotics", "Game Playing", "Data Mining", "Fraud Detection", "Medical Diagnosis", "Financial Trading", "Content Moderation", "Customer Service", "Energy", "Manufacturing", "Security","Transportation","Weather Forecasting"], 
    "Search Engines": ["google", "bing", "yahoo", "search engine"],
    "Adult Content": ["porn", "adult", "xxx"],
    "Programming": ["programming", "coding", "developer", "code", "software development", "web development", "mobile development", "frontend", "backend", "full-stack", "devops", "API", "frameworks", "libraries", "programming languages", "source control", "debugging", "testing"],
    "SBC": ["raspberry pi", "arduino", "single board computer"],
    "Entertainment": ["movies", "tv", "music", "streaming"],
    "Computers": ["computer", "laptop", "hardware", "software"],
    "Magazines": ["magazine", "journal", "periodical"],
    "Other": [],
    "Unknown": [],
    "Shopping": ["shop", "store", "ecommerce", "buy", "purchase"],
    # Add more categories and associated keywords or domain names here
}

def categorize_url(url: str, categories: dict) -> str:
    main_url = tldextract.extract(url).domain  # Use tldextract to get the domain
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in main_url.lower():
                return category
    return "Uncategorized"



def fetch_url_content(url: str) -> str:
    """Fetches the content of the given URL."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Request failed with exception: {e}")
    
    if response.status_code == 200:
        return response.text
    elif response.status_code in (403, 404, 410, 429, 522):
        raise requests.exceptions.RequestException(
            f"Request failed with status code {response.status_code}"
        )
    else:
        raise requests.exceptions.RequestException(
            f"Request failed with status code {response.status_code}"
        )

def extract_metadata(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, "lxml")
    metadata = {}

    # Extract title
    title = soup.find("title")
    if title:
        metadata["title"] = title.text

    # Extract description
    description = soup.find("meta", attrs={"name": "description"})
    if description and "content" in description.attrs:
        metadata["description"] = description["content"]

    # Extract Open Graph image
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image and "content" in og_image.attrs:
        metadata["image"] = og_image["content"]

    return metadata




def extract_favicon_url(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "lxml")
    favicon = soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")
    if favicon:
        return favicon["href"]
    return ""

def check_favicon_url(url: str) -> bool:
    try:
        response = requests.head(url, timeout=10)  # Add a timeout argument
        if response.status_code == 200 and response.headers["content-type"].startswith("image"):
            return True
    except requests.exceptions.RequestException:
        pass
    return False

def create_readme_md(urls: List[str], output_dir: str):
    h2t = html2text.HTML2Text()
    h2t.ignore_links = True
    h2t.ignore_images = True
    error_list = []

    entries_by_category = defaultdict(list)

    for i, url in enumerate(tqdm(urls, desc="Processing URLs")):
        try:
            content = fetch_url_content(url)
            metadata = extract_metadata(content)
            favicon_url = extract_favicon_url(content)

            entry = ""

            if favicon_url and check_favicon_url(favicon_url):
                entry += f"![Favicon]({favicon_url}) "

            entry += f"[{metadata.get('title', url)}]({url})\n\n"

            if "description" in metadata:
                entry += f"{h2t.handle(metadata['description'])}\n\n"

            category = categorize_url(url, categories)

            entries_by_category[category].append((metadata.get('title', url), entry))

        except requests.exceptions.RequestException as e:
            error_list.append(f"Error processing {url}: {e}")
#            print(f"Error processing {url}: {e}")

    with open(os.path.join(output_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write("# My Bookmarks\n\n")

        for category, entries in entries_by_category.items():
            f.write(f"## {category}\n\n")
            entries.sort()
            for _, entry in entries:
                f.write(entry)
            f.write("\n")  # Add an extra line break to separate categories

        if error_list:
            f.write("## Errors\n\n")
            f.write("The following URLs could not be processed due to errors:\n\n")
            for error in error_list:
                f.write(f"- {error}\n")
            f.write("\n")

def extract_urls_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, "html.parser")
    urls = [a["href"] for a in soup.find_all("a", href=True)]
    return urls

def main():
    parser = argparse.ArgumentParser(
        description="Process HTML bookmarks file and generate README.md with metadata."
    )
    parser.add_argument("bookmarks_file", help="Path to the HTML bookmarks file.")

    args = parser.parse_args()

    # Get the script's directory
    script_dir = os.path.dirname(os.path.realpath(__file__))

    urls = extract_urls_from_html(args.bookmarks_file)

    if urls:
        create_readme_md(urls, script_dir)  # Pass script_dir instead of output_dir
    else:
        print(f"No URLs found in {args.bookmarks_file}")

if __name__ == "__main__":
    main()
