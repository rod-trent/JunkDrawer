# Gift Genius: I Finally Stole My Son’s Superpower (with a little help from Grok)

For years I’ve lived in the shadow of the greatest gift-giver on planet Earth: my oldest son.

This kid is spooky. You mention once, in passing, that you kind of like mechanical keyboards? Christmas morning there’s a custom-built 75% with lubed Gateron Ink Blacks under the tree. Your friend says they’re “sort of getting into film photography”? He somehow finds a perfectly serviced Contax T2 in Kyoto, has it shipped, and wraps it like it was no big deal. He doesn’t guess—he *knows*.  

I, on the other hand, am the guy who buys socks. Nice socks… but still socks.

So I did what any self-respecting dad-who-can-code does: I built an app that cheats.

Meet **Gift Genius**—a tiny Streamlit app that turns a public X (Twitter) or Instagram profile into five scarily spot-on gift ideas, powered entirely by Grok-3.

### What It Is

You give it a public @username (no @ sign needed).  
It quietly pulls their recent posts.  
Grok reads them like a mind-reader and returns five thoughtful, specific gifts they’ll actually love—complete with price range, why it fits (with references to their posts), and where to buy.

Think of it as hiring my son’s brain for ten seconds, except it costs $0 in API fees if you stay within limits and works for anyone with a public social profile.

### The Origin Story (a.k.a. Dad Jealousy)

Every December I watch my son nail gift after gift while I panic-order Amazon Prime desperation presents at 2 a.m. Last year I decided enough was enough. If I can’t naturally develop this talent, I’ll engineer it.

The result is Gift Genius. It’s my love letter to his gift-giving genius—and my attempt to level the playing field with AI.

### How to Use It (takes ~30 seconds)

1. Grab a free Grok API key at https://console.x.ai
2. `pip install streamlit python-dotenv httpx instaloader`
3. Clone the repo or copy the single `gifter.py` file
4. Create a `.env` file with  
   `GROK_API_KEY=your_key_here`
5. `streamlit run gifter.py`
6. Pick X or Instagram → type a public username → hit “Analyze & Recommend Gifts”
7. Watch Grok do the scary-accurate thing

Try it with @elonmusk, @taylorswift13, @natgeo, or literally any public account. The results are… honestly kind of terrifying in the best way.

### How It Works Under the Hood

- **X (Twitter)**: Instead of dealing with Twitter’s API apocalypse, I just ask Grok itself to search the user and fetch the latest 20 posts using its built-in tools (`x_user_search` + `x_keyword_search`). Zero extra libraries, zero rate limits, zero pain.
- **Instagram**: Falls back to good old Instaloader (still works great for public profiles in 2025).
- The posts are concatenated and fed to a second Grok-3 call with a carefully crafted prompt that forces warm, creative, markdown-rich gift recommendations.
- Everything runs locally in Streamlit—no backend, no database, no funny business.

### Example in Action

I tested it on myself (@yourhandlehere). Grok noticed I keep posting about coffee, fountain pens, and retro gaming. The suggestions?

1. A limited-run ceramic dripper from a Japanese pottery studio ($120–180)  
2. Sailor 1911L with a custom nib grind from Tokyo ($320–400)  
3. Analogue Pocket with the openFPGA Mario core pre-loaded ($280)  

…My wife is now terrified because she used the app on me.

### Closing Thought

My son still has the edge—he’ll always add that perfect hand-written card and wrap it like a work of art. But for the first time in my life, I’m walking into Christmas without the annual “gift anxiety” sweat.

If you’ve ever felt gift-blocked, try Gift Genius. And if you’re already a natural like my oldest… well, consider this my formal surrender.

Link to the code: github.com/yourname/gift-genius (I’ll push it right after posting this)

Happy gifting—and may all your presents finally be as good as my kid’s. 🎁
