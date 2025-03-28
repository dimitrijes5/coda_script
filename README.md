# Coda Document HTML Scraper and Converter

This project provides a set of tools to:
1. Scrape HTML content from Coda documents
2. Convert the exported HTML files to structured JSON format

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/coda-scrape-insert.git
cd coda-scrape-insert
```

2. Install the required dependencies:
```bash
pip install beautifulsoup4 requests
```

## Usage

### Running the Tool
Run the main script and choose an operation:

```bash
python3 main.py
```

You will be prompted to select one of the following operations:
1. Scrape Coda pages
2. Convert HTML files to JSON

### Scraping Coda Pages

The scraper uses the Coda API to fetch and download document pages as HTML. To use this feature:

1. Make sure you have a `pages.json` file with the list of pages to scrape
2. The script will generate download links and save them to `download_links.txt`
3. You'll be prompted to open these links in your browser

### Converting HTML to JSON

This tool converts HTML files stored in the `html_pages` directory to a structured JSON format:

1. Place your HTML files in the `html_pages` directory
2. Run the converter
3. The generated JSON will be saved as `posts.json`

## Structure

The converter parses HTML into a structured JSON format with the following elements:
- Paragraphs with text alignment
- Headings with proper level and alignment
- Lists (ordered and unordered)
- Text formatting attributes (bold, italic, underline, font size)

## Example Output

```json
{
  "Title": "Page Title",
  "Slug": "page-title",
  "Content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "attrs": {"textAlign": "left"},
        "content": [
          {
            "type": "text",
            "text": "Sample text with ",
          },
          {
            "type": "text",
            "text": "bold formatting",
            "marks": [{"type": "bold"}]
          }
        ]
      }
    ]
  }
}
```

## Files

- `main.py`: Main entry point for the application
- `coda_scraper.py`: Contains the Coda API integration and scraping functionality
- `html_converter.py`: Handles HTML parsing and conversion to JSON format

## License

MIT 