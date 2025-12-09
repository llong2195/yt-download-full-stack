"""Test bulk channel import feature."""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_import_channels():
    """Test the bulk import endpoint."""
    
    # Sample import data
    raw_text = """TechChannel|https://www.youtube.com/@mkbhd|/downloads/tech
GameChannel|https://www.youtube.com/@pewdiepie|/downloads/games
MusicChannel|https://www.youtube.com/@vevo|"""
    
    # Make request to import endpoint
    response = requests.post(
        f"{BASE_URL}/api/channels/import",
        json={"raw_text": raw_text},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n=== Import Summary ===")
        print(f"Total: {data['total']}")
        print(f"Created: {data['created']}")
        print(f"Updated: {data['updated']}")
        print(f"Failed: {data['failed']}")
        
        print(f"\n=== Detailed Results ===")
        for result in data['results']:
            status_emoji = {
                'created': '✅',
                'updated': '🔄',
                'failed': '❌'
            }
            emoji = status_emoji.get(result['status'], '❓')
            print(f"{emoji} Line {result['line_number']}: {result['name']} - {result['status']}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
            if result.get('channel_id'):
                print(f"   Channel ID: {result['channel_id']}")
    else:
        print(f"Error: {response.text}")


def test_import_with_errors():
    """Test import with some invalid lines."""
    
    raw_text = """ValidChannel|https://www.youtube.com/@mkbhd|/downloads/valid
InvalidFormat|no-pipe-here
|https://www.youtube.com/@test|/downloads/test
EmptyName||/downloads/empty
BadURL|https://not-youtube.com/channel/test|/downloads/bad"""
    
    response = requests.post(
        f"{BASE_URL}/api/channels/import",
        json={"raw_text": raw_text},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n\n=== Test with Errors ===")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Created: {data['created']}, Updated: {data['updated']}, Failed: {data['failed']}")
        
        for result in data['results']:
            if result['status'] == 'failed':
                print(f"❌ Line {result['line_number']}: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    print("Testing Bulk Channel Import Feature")
    print("=" * 50)
    
    try:
        test_import_channels()
        test_import_with_errors()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
