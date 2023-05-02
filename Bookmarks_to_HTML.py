import argparse
import os
import requests
from bs4 import BeautifulSoup
from typing import List
from tqdm import tqdm

def fetch_url_content(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
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
    if description:
        metadata["description"] = description["content"]

    # Extract Open Graph image
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image:
        metadata["image"] = og_image["content"]

    # Extract favicon
    favicon = soup.find("link", rel="icon")
    if favicon:
        metadata["favicon"] = favicon["href"]
    else:
        favicon = soup.find("link", rel="shortcut icon")
        if favicon:
            metadata["favicon"] = favicon["href"]

    return metadata


def extract_urls_from_html(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "lxml")
    urls = [a["href"] for a in soup.find_all("a", href=True)]

    return urls

def create_output_html(urls: List[str], output_filename: str):
    error_list = []

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html lang="en">\n')
        f.write('<head>\n')
        f.write('<meta charset="UTF-8">\n')
        f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
        f.write('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write('<div class="container">\n')
        f.write('<div class="row">\n')

        for url in tqdm(sorted(urls), desc="Processing URLs"):
            try:
                content = fetch_url_content(url)
                metadata = extract_metadata(content)

                f.write('<div class="col-md-4 mb-4">\n')
                f.write('<div class="card">\n')
                if "image" in metadata:
                    f.write(f'<a href="{url}" target="_blank"><img src="{metadata["image"]}" class="card-img-top" alt="{metadata.get("title", "No Title")}" loading="lazy"></a>\n')
                f.write('<div class="card-body">\n')
                f.write(f'<a href="{url}" target="_blank">\n')
                if "favicon" in metadata:
                    f.write(f'<img src="{metadata["favicon"]}" alt="Favicon" style="width: 16px; height: 16px;"> ')
                f.write(f'<h5 class="card-title d-inline">{metadata.get("title", "No Title")}</h5>\n')
                f.write(f'<p class="card-text">{metadata.get("description", "No Description")}</p>\n')
                f.write('</a>\n')
                f.write('</div>\n')
                f.write('</div>\n')
                f.write('</div>\n')

            except requests.exceptions.RequestException as e:
                error_list.append(f"Error processing {url}: {e}")

        f.write('</div>\n')  # Close the row
        f.write('</div>\n')  # Close the container

        # Write errors at the end of the file
        if error_list:
            f.write('<div class="container">\n')
            f.write('<h3>Errors</h3>\n')
            f.write('<ul>\n')
            for error in error_list:
                f.write(f'<li>{error}</li>\n')
            f.write('</ul>\n')
            f.write('</div>\n')

        f.write('</body>\n')
        f.write('</html>\n')


def main():
    parser = argparse.ArgumentParser(
        description="Process HTML bookmarks file and generate a styled HTML output file."
    )
    parser.add_argument("bookmarks_file", help="Path to the HTML bookmarks file.")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.realpath(__file__))
    urls = extract_urls_from_html(args.bookmarks_file)

    if urls:
        output_filename = os.path.splitext(args.bookmarks_file)[0] + "-Styled.html"
        create_output_html(urls, output_filename)
    else:
        print(f"No URLs found in {args.bookmarks_file}")

if __name__ == "__main__":
    main()
