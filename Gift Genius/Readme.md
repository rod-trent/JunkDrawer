# Gift Genius: I Finally Stole My Son’s Superpower  
(And Now It Lives Permanently on GitHub)

For years I’ve been hopelessly outclassed by the greatest gift-giver alive: my oldest son.

You casually mention you’re “thinking about getting into espresso”? Boom—three days later a niche lever machine from 1970s Italy appears, restored, with a handwritten note about tamp pressure. Your cousin says she misses film photography? He tracks down a mint Leica M6 with the exact lens she drooled over in 2009. The kid doesn’t guess—he performs psychic surgery on your soul and pulls out the perfect object.

Me? I’m the guy who buys the wrong size Yeti rambler. Every. Single. Year.

So I did the only rational thing: I built an app that gives me his superpower on demand.

Say hello to **Gift Genius**—a dead-simple Streamlit app that turns any public X (Twitter) or Instagram profile into five terrifyingly accurate, heartfelt gift ideas in under a minute.

### Permanent Home
The app now lives forever right here:  
https://github.com/rod-trent/JunkDrawer/tree/main/Gift%20Genius

Everything you need is in that folder:
- `gifter.py` – the main Streamlit app
- `utils/social_scraper.py` – Instagram fetching logic (using battle-tested Instaloader)
- `.env.example` – just drop in your Grok API key and go

### How to Run It (30-second setup)

```bash
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/Gift Genius
pip install streamlit python-dotenv httpx instaloader
cp .env.example .env
# paste your Grok API key into .env
streamlit run gifter.py
```

That’s it. You now possess the same dark art my son has been wielding against the family for a decade.

### Where It Shines in Real Life

Most of my family and friends abandoned X years ago. They live on Instagram—posting Stories of their new hobby, weekend hikes, obscure vinyl finds, or their dog in increasingly ridiculous outfits. Gift Genius reads all of it like a best friend who never forgets anything you’ve ever said.

I’ve used it on:
- My sister-in-law who only posts sourdough and plants → got a rare Japanese shibo pot and a $300 grow-light sculpture she still talks about
- My brother who’s deep into mechanical watches on IG → a limited Sinn U50 “S” that actually made him tear up
- My niece whose entire personality is Taylor Swift concert footage → custom Eras Tour embroidery on a vintage denim jacket

Every single one felt like my son had picked it… because in a way, he finally taught me how.

### Under the Hood (Nerd Section)

- X posts → fetched directly by asking Grok-3 to use its own built-in `x_user_search` + `x_keyword_search` tools. No Twitter API keys, no rate-limit tears.
- Instagram posts → pulled cleanly by `utils/social_scraper.py` using Instaloader (still rock-solid for public profiles in 2025).
- Final gift recommendations → one spicy Grok-3 call with a prompt I’ve been refining for months. Temperature 0.85 for warmth and creativity, but still grounded in the actual posts.

### Closing Thought

My son will always be the undisputed champion—he adds the card, the story, the perfect bow. But for the first time ever, I’m not sweating December like it’s a second mortgage.

If you’ve ever stared at someone’s wishlist (or lack thereof) in quiet panic, steal my cheat code.

Gift Genius is public, free, and waiting for you:  
https://github.com/rod-trent/JunkDrawer/tree/main/Gift%20Genius

Go forth and give like the favorite child you secretly wish you were.

(And son, if you’re reading this… yes, I finally caught up. Love you.) 🎁
