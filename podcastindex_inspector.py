#!/usr/bin/env python3
"""
Podcastindex Inspector - A tool to identify duplicate podcast episodes in the Podcastindex database
"""

import os
import sys
import time
import json
import hashlib
import argparse
import configparser
import requests
from typing import Dict, List, Optional, Tuple

class PodcastIndexAPI:
    """Class to interact with the Podcastindex API"""
    
    BASE_URL = "https://api.podcastindex.org/api/1.0"
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize with API credentials"""
        self.api_key = api_key
        self.api_secret = api_secret
    
    def _get_auth_headers(self) -> Dict:
        """Generate authentication headers for API requests"""
        epoch_time = int(time.time())
        data_to_hash = self.api_key + self.api_secret + str(epoch_time)
        sha_1 = hashlib.sha1(data_to_hash.encode()).hexdigest()
        
        return {
            'X-Auth-Date': str(epoch_time),
            'X-Auth-Key': self.api_key,
            'Authorization': sha_1,
            'User-Agent': 'PodcastindexInspector/1.0'
        }
    
    def get_podcast_by_feed_url(self, feed_url: str) -> Dict:
        """Get podcast information by feed URL"""
        endpoint = f"{self.BASE_URL}/podcasts/byfeedurl"
        params = {'url': feed_url}
        
        try:
            response = requests.get(
                endpoint,
                headers=self._get_auth_headers(),
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Error getting podcast: {response.status_code} - {response.text}")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request error when getting podcast: {e}")
    
    def get_podcast_by_feed_id(self, feed_id: int) -> Dict:
        """Get podcast information by feed ID"""
        endpoint = f"{self.BASE_URL}/podcasts/byfeedid"
        params = {'id': feed_id}
        
        try:
            response = requests.get(
                endpoint,
                headers=self._get_auth_headers(),
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Error getting podcast: {response.status_code} - {response.text}")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request error when getting podcast: {e}")
    
    def get_episodes_by_feed_id(self, feed_id: int, max_results: int = 1000) -> Dict:
        """Get episodes for a podcast by feed ID"""
        endpoint = f"{self.BASE_URL}/episodes/byfeedid"
        params = {'id': feed_id, 'max': max_results}
        
        try:
            response = requests.get(
                endpoint,
                headers=self._get_auth_headers(),
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Error getting episodes: {response.status_code} - {response.text}")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request error when getting episodes: {e}")


class PodcastInspector:
    """Main class for identifying duplicate podcast episodes"""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize with API credentials"""
        self.api = PodcastIndexAPI(api_key, api_secret)
    
    def get_podcast_by_feed_url(self, feed_url: str) -> Dict:
        """Get podcast information by feed URL"""
        response = self.api.get_podcast_by_feed_url(feed_url)
        
        if response.get('status') != 'true':
            raise Exception(f"Error getting podcast: {response.get('description')}")
        
        return response.get('feed', {})
    
    def get_podcast_by_feed_id(self, feed_id: int) -> Dict:
        """Get podcast information by feed ID"""
        response = self.api.get_podcast_by_feed_id(feed_id)
        
        if response.get('status') != 'true':
            raise Exception(f"Error getting podcast: {response.get('description')}")
        
        return response.get('feed', {})
    
    def get_episodes_by_feed_id(self, feed_id: int, max_results: int = 1000) -> List[Dict]:
        """Get episodes for a podcast by feed ID"""
        response = self.api.get_episodes_by_feed_id(feed_id, max_results)
        
        if response.get('status') != 'true':
            raise Exception(f"Error getting episodes: {response.get('description')}")
        
        return response.get('items', [])
    
    def find_duplicate_episodes(self, episodes: List[Dict]) -> Dict[str, List[Dict]]:
        """Find duplicate episodes based on title or episode number"""
        episodes_by_title = {}
        episodes_by_number = {}
        
        # Group episodes by title
        for episode in episodes:
            title = episode.get('title', '').strip()
            if title:
                if title not in episodes_by_title:
                    episodes_by_title[title] = []
                episodes_by_title[title].append(episode)
        
        # Group episodes by episode number
        for episode in episodes:
            episode_num = episode.get('episode')
            if episode_num:
                if episode_num not in episodes_by_number:
                    episodes_by_number[episode_num] = []
                episodes_by_number[episode_num].append(episode)
        
        # Filter to only include duplicates
        duplicate_titles = {title: episodes for title, episodes in episodes_by_title.items() if len(episodes) > 1}
        duplicate_numbers = {number: episodes for number, episodes in episodes_by_number.items() if len(episodes) > 1}
        
        return {
            'by_title': duplicate_titles,
            'by_number': duplicate_numbers
        }
    
    def print_episodes(self, episodes: List[Dict]) -> None:
        """Print episode information"""
        print(f"\nFound {len(episodes)} episodes:")
        
        for i, episode in enumerate(episodes, 1):
            print(f"{i}. ID: {episode.get('id')}")
            print(f"   Title: {episode.get('title')}")
            print(f"   Date: {episode.get('datePublished')}")
            print(f"   Episode #: {episode.get('episode')}")
            print(f"   URL: {episode.get('enclosureUrl')}")
            print()
    
    def print_duplicates(self, duplicates: Dict[str, List[Dict]]) -> None:
        """Print duplicate episodes"""
        duplicate_titles = duplicates['by_title']
        duplicate_numbers = duplicates['by_number']
        
        if not duplicate_titles and not duplicate_numbers:
            print("No duplicate episodes found.")
            return
        
        print("\n=== Duplicate Episodes ===\n")
        
        if duplicate_titles:
            print("Duplicates by title:")
            for title, episodes in duplicate_titles.items():
                print(f"\nTitle: {title}")
                for i, episode in enumerate(episodes, 1):
                    print(f"  {i}. ID: {episode.get('id')}")
                    print(f"     Date: {episode.get('datePublished')}")
                    print(f"     Episode #: {episode.get('episode')}")
                    print(f"     URL: {episode.get('enclosureUrl')}")
        
        if duplicate_numbers:
            print("\nDuplicates by episode number:")
            for number, episodes in duplicate_numbers.items():
                print(f"\nEpisode #: {number}")
                for i, episode in enumerate(episodes, 1):
                    print(f"  {i}. ID: {episode.get('id')}")
                    print(f"     Title: {episode.get('title')}")
                    print(f"     Date: {episode.get('datePublished')}")
                    print(f"     URL: {episode.get('enclosureUrl')}")
    
    def export_duplicates(self, duplicates: Dict[str, List[Dict]]) -> None:
        """Export duplicate episodes to a JSON file"""
        duplicate_titles = duplicates['by_title']
        duplicate_numbers = duplicates['by_number']
        
        if not duplicate_titles and not duplicate_numbers:
            print("No duplicate episodes found to export.")
            return
        
        # Create a list to store episodes to export
        episodes_to_export = []
        
        # Add duplicates by title
        for title, episodes in duplicate_titles.items():
            for episode in episodes:
                episodes_to_export.append({
                    'id': episode.get('id'),
                    'title': episode.get('title'),
                    'episode_number': episode.get('episode'),
                    'date_published': episode.get('datePublished'),
                    'url': episode.get('enclosureUrl'),
                    'duplicate_type': 'title',
                    'duplicate_value': title
                })
        
        # Add duplicates by episode number
        for number, episodes in duplicate_numbers.items():
            for episode in episodes:
                # Check if this episode is already in the export list (from title duplicates)
                episode_id = episode.get('id')
                if not any(e['id'] == episode_id for e in episodes_to_export):
                    episodes_to_export.append({
                        'id': episode_id,
                        'title': episode.get('title'),
                        'episode_number': episode.get('episode'),
                        'date_published': episode.get('datePublished'),
                        'url': episode.get('enclosureUrl'),
                        'duplicate_type': 'episode_number',
                        'duplicate_value': number
                    })
        
        # Export episodes to a file
        export_file = f"podcast_episodes_export_{int(time.time())}.json"
        print(f"\nExporting {len(episodes_to_export)} episodes to {export_file}")
        with open(export_file, 'w') as f:
            json.dump(episodes_to_export, f, indent=2)
        print(f"Export complete. You can use this file for manual handling of episodes.")
        print("Note: The Podcastindex API does not support direct episode deletion or updates through their public API.")
        print("If you need to remove or update duplicate episodes, please contact Podcastindex support with the specific episode IDs.")


def setup_config():
    """Set up configuration file for API credentials"""
    config = configparser.ConfigParser()
    config_file = 'podcastindex_config.ini'
    
    # Check if config file exists
    if os.path.exists(config_file):
        config.read(config_file)
        
        # Check if API credentials are in config
        if 'API' in config and 'key' in config['API'] and 'secret' in config['API']:
            return config['API']['key'], config['API']['secret']
    
    # If not, prompt for API credentials
    print("Podcastindex API credentials not found. Please enter them below:")
    api_key = input("API Key: ")
    api_secret = input("API Secret: ")
    
    # Save credentials to config file
    config['API'] = {
        'key': api_key,
        'secret': api_secret
    }
    
    with open(config_file, 'w') as f:
        config.write(f)
    
    return api_key, api_secret


def main():
    """Main function to run the script"""
    parser = argparse.ArgumentParser(description='Identify duplicate podcast episodes in the Podcastindex database')
    
    parser.add_argument('--feed-url', help='URL of the podcast feed to manage')
    parser.add_argument('--feed-id', type=int, help='ID of the podcast feed to manage')
    parser.add_argument('--list', action='store_true', help='List all episodes for the podcast')
    parser.add_argument('--find-duplicates', action='store_true', help='Find duplicate episodes')
    parser.add_argument('--export-only', action='store_true', help='Export duplicate episodes to a JSON file')
    
    args = parser.parse_args()
    
    # Check if at least one required argument is provided
    if not args.feed_url and not args.feed_id:
        parser.error("Either --feed-url or --feed-id is required")
    
    # Set up API credentials
    api_key, api_secret = setup_config()
    
    # Create podcast inspector
    inspector = PodcastInspector(api_key, api_secret)
    
    try:
        # Get podcast information
        if args.feed_url:
            print(f"Getting podcast information for feed URL: {args.feed_url}")
            podcast = inspector.get_podcast_by_feed_url(args.feed_url)
        else:
            print(f"Getting podcast information for feed ID: {args.feed_id}")
            podcast = inspector.get_podcast_by_feed_id(args.feed_id)
        
        print(f"\nPodcast: {podcast.get('title')}")
        print(f"Feed ID: {podcast.get('id')}")
        print(f"URL: {podcast.get('url')}")
        
        # Get episodes
        feed_id = podcast.get('id')
        print(f"\nGetting episodes for feed ID: {feed_id}")
        episodes = inspector.get_episodes_by_feed_id(feed_id)
        
        # List episodes if requested
        if args.list:
            inspector.print_episodes(episodes)
        
        # Find and print duplicates if requested
        if args.find_duplicates:
            duplicates = inspector.find_duplicate_episodes(episodes)
            inspector.print_duplicates(duplicates)
            
            # Export duplicates if requested
            if args.export_only:
                inspector.export_duplicates(duplicates)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
