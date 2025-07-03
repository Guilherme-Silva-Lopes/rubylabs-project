import asyncio
import csv
import logging
from typing import List, Dict, Any

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = "https://jsonplaceholder.typicode.com"
USERS_URL = f"{BASE_URL}/users"
POSTS_URL = f"{BASE_URL}/posts"
COMMENTS_URL = f"{BASE_URL}/comments"
OUTPUT_CSV_PATH = "output.csv"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def fetch_json(session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
    """
    Fetches JSON data from a URL with retries on failure.
    """
    logging.info(f"Fetching data from {url}")
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            logging.info(f"Successfully fetched data from {url}")
            return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f"API call to {url} failed: {e}")
        raise


async def get_users(session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    """
    Fetches all users and filters for those with even IDs.
    """
    users = await fetch_json(session, USERS_URL)
    return [user for user in users if user.get("id") % 2 == 0]


async def get_latest_posts_for_user(session: aiohttp.ClientSession, user_id: int) -> List[Dict[str, Any]]:
    """
    Fetches the 5 latest posts for a given user.
    """
    posts_url = f"{POSTS_URL}?userId={user_id}"
    posts = await fetch_json(session, posts_url)
    # Sort by ID descending to get the latest posts
    return sorted(posts, key=lambda x: x.get("id"), reverse=True)[:5]


async def get_latest_comments_for_post(session: aiohttp.ClientSession, post_id: int) -> List[Dict[str, Any]]:
    """
    Fetches the 3 latest comments for a given post.
    """
    comments_url = f"{COMMENTS_URL}?postId={post_id}"
    comments = await fetch_json(session, comments_url)
    # Sort by ID descending to get the latest comments
    return sorted(comments, key=lambda x: x.get("id"), reverse=True)[:3]


def validate_data(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validates that the given data contains all required fields.
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            logging.warning(f"Validation failed: Missing or invalid field '{field}' in {data}")
            return False
    return True


async def process_user_data(session: aiohttp.ClientSession, user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Processes a single user's data to fetch posts and comments.
    """
    if not validate_data(user, ["id", "name"]):
        return []

    user_id = user["id"]
    posts = await get_latest_posts_for_user(session, user_id)
    user_comments = []

    for post in posts:
        if not validate_data(post, ["id", "title"]):
            continue

        comments = await get_latest_comments_for_post(session, post["id"])
        for comment in comments:
            if not validate_data(comment, ["id", "body", "email"]):
                continue

            user_comments.append({
                "user_id": user_id,
                "user_name": user["name"],
                "post_id": post["id"],
                "post_title": post["title"],
                "comment_id": comment["id"],
                "comment_body": comment["body"],
                "comment_author_email": comment["email"],
            })

    return user_comments


async def main():
    """
    Main function to fetch, process, and save the data.
    """
    async with aiohttp.ClientSession() as session:
        users = await get_users(session)
        
        tasks = [process_user_data(session, user) for user in users]
        results = await asyncio.gather(*tasks)
        
        all_comments_data = [item for sublist in results for item in sublist]

    # Write to CSV
    if all_comments_data:
        with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "user_id", "user_name", "post_id", "post_title", 
                "comment_id", "comment_body", "comment_author_email"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_comments_data)
        logging.info(f"Data successfully written to {OUTPUT_CSV_PATH}")
    else:
        logging.info("No data to write to CSV.")


if __name__ == "__main__":
    asyncio.run(main())
