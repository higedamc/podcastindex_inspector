# Podcastindex Inspector

A tool to help identify duplicate podcast episodes in the Podcastindex database.

## Overview

This script allows you to:

1. Authenticate with the Podcastindex API
2. Retrieve podcast episodes
3. Identify duplicate episodes
4. Export duplicate episode data for manual handling

## Requirements

- Python 3.6+
- Required packages (install using `pip install -r requirements.txt`):
  - requests
  - configparser

## Setup

1. Clone or download this repository
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Get your API credentials from Podcastindex.org:
   - Sign up at [https://api.podcastindex.org/](https://api.podcastindex.org/)
   - Create an API key and secret

## Usage

The script can be run with various command-line arguments:

```bash
python podcastindex_inspector.py [options]
```

### Options

- `--feed-url URL`: Specify the URL of your podcast feed
- `--feed-id ID`: Specify the Podcastindex feed ID (if you know it)
- `--list`: List all episodes for the podcast
- `--find-duplicates`: Find and display duplicate episodes
- `--export-only`: Export episode data to a JSON file for manual handling

### Examples

1. List all episodes for a podcast:

   ```bash
   python podcastindex_inspector.py --feed-url https://example.com/feed.xml --list
   ```

2. Find duplicate episodes:

   ```bash
   python podcastindex_inspector.py --feed-url https://example.com/feed.xml --find-duplicates
   ```

3. Export duplicate episodes to a JSON file:

   ```bash
   python podcastindex_inspector.py --feed-url https://example.com/feed.xml --find-duplicates --export-only
   ```

## How It Works

The script identifies duplicate episodes based on:

1. Identical titles
2. Identical episode numbers

When duplicates are found, the script can export the episode data to a JSON file, which you can use to:
- Keep track of duplicate episodes
- Contact Podcastindex support with specific episode IDs
- Handle the duplicates through other means

## Note on API Limitations

The Podcastindex API does not currently support direct episode deletion or updates through their public API. If you need to remove or update duplicate episodes, you'll need to contact Podcastindex support with the specific episode IDs.

## Troubleshooting

### API Credentials

If you encounter authentication errors, check that your API key and secret are correct. The script stores these in a configuration file (`podcastindex_config.ini`) after the first run.

### Rate Limiting

The Podcastindex API may have rate limits. If you encounter rate limiting errors, wait a while before trying again.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
