# utils/social_scraper.py
import instaloader
import time

def get_instagram_posts(username: str, limit: int = 15) -> list[str]:
    """Fetch public Instagram captions using Instaloader (2025-proof, no login)."""
    if not username:
        return ["Username required."]

    L = instaloader.Instaloader(
        quiet=True,
        sleep=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    try:
        profile = instaloader.Profile.from_username(L.context, username)

        if profile.is_private:
            return ["Instagram profile is private."]

        posts = []
        for post in profile.get_posts():
            if len(posts) >= limit:
                break
            caption = (post.caption or post.accessibility_caption or "").strip()
            if caption:
                posts.append(caption)
            time.sleep(1)  # Be nice to Instagram

        return posts if posts else ["No public captions found."]

    except instaloader.exceptions.ProfileNotExistsException:
        return [f"Instagram profile @{username} does not exist."]
    except Exception as e:
        return [f"Instagram error: {str(e)}"]