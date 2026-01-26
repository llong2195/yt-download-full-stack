"""Example of using the check_downloads API endpoint.

This example demonstrates how to check if multiple YouTube videos
have been downloaded using the /api/downloads/check_downloads endpoint.
"""

import requests
import json


def check_downloads_example():
    """Example usage of the check_downloads API."""

    # API endpoint
    url = "http://localhost:8000/api/downloads/check_downloads"

    # Example video URLs to check
    payload = {
        "urls": [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/jNQXAC9IVRw",
            "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "https://m.youtube.com/watch?v=kJQP7kiw5Fk",
        ]
    }

    try:
        # Make POST request
        response = requests.post(url, json=payload)
        response.raise_for_status()

        # Parse response
        data = response.json()

        print("=== Check Downloads Results ===\n")
        print(f"Total checked: {data['total_checked']}")
        print(f"Total downloaded: {data['total_downloaded']}\n")

        print("Detailed Results:")
        print("-" * 80)

        for result in data["results"]:
            url = result["url"]
            video_id = result.get("video_id", "N/A")
            is_downloaded = result["is_downloaded"]

            if is_downloaded:
                print(f"✓ {url}")
                print(f"  Video ID: {video_id}")
                print(f"  Title: {result.get('video_title', 'N/A')}")
                print(f"  Downloaded: {result.get('download_date', 'N/A')}")
                print(f"  File Path: {result.get('file_path', 'N/A')}")
            else:
                print(f"✗ {url}")
                print(f"  Video ID: {video_id}")
                print(f"  Status: Not downloaded")
                if result.get("error"):
                    print(f"  Error: {result['error']}")

            print("-" * 80)

        return data

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the backend server is running on http://localhost:8000")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")


def check_single_video(video_url):
    """Check if a single video has been downloaded."""

    url = "http://localhost:8000/api/downloads/check_downloads"
    payload = {"urls": [video_url]}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        result = data["results"][0]

        print(f"\nChecking: {video_url}")

        if result["is_downloaded"]:
            print(f"✓ Video is downloaded")
            print(f"  Title: {result.get('video_title')}")
            print(f"  Path: {result.get('file_path')}")
        else:
            print(f"✗ Video is not downloaded")
            if result.get("error"):
                print(f"  Error: {result['error']}")

        return result

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Example 1: Check multiple videos")
    print("=" * 80)
    check_downloads_example()

    print("\n\nExample 2: Check single video")
    print("=" * 80)
    check_single_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
