![JSON Converter](https://raw.githubusercontent.com/rod-trent/JunkDrawer/refs/heads/main/JSON_Converter/Images/workingwithjson.jpg "JSON Converter")

# My Favorite Offline JSON Formatter: A Tool I Built and Actually Use Every Day

Hi, I'm Rod Trent – yes, the guy behind the somewhat chaotically named *JunkDrawer* repo on GitHub.

Over the years I’ve thrown hundreds of random scripts, KQL queries, one-liners, and little utilities in there. Most of them are quick-and-dirty things I needed during a Sentinel incident, a customer call, or while staring at yet another unreadable blob of JSON at 2 a.m.

One of those files has apparently gotten a life of its own: **JSONFormatter.html**

Direct link: https://github.com/rod-trent/JunkDrawer/blob/main/JSON_Converter/JSONFormatter.html

### Why I originally built it

I got tired of:

- Pasting potentially sensitive logs into random online JSON prettifiers
- Being on air-gapped networks or customer environments with zero internet
- Waiting for bloated web apps to load just to format a 3 MB blob
- Online tools that choke on large objects or have character limits

So I built the simplest thing that could possibly work: a single HTML file that does everything client-side. No dependencies, no frameworks, no telemetry, no nonsense.

Download it once, open it anywhere, forever.

### What it actually does (2025 edition – still just one file)

- Pretty-print / beautify with 2, 3, 4 spaces or tabs
- Minify/compress
- Full JSON validation with precise line/column error reporting
- Interactive collapsible tree view (my personal favorite)
- Built-in search across keys and values
- Light/dark mode toggle
- Optional alphabetical sorting of object keys
- Load from file or paste
- Copy or download the result
- Works completely offline after the first download

I still open this thing literally every single day – whether I’m cleaning up a massive Microsoft Sentinel query result, formatting API responses, or helping someone debug a logic app.

### How to grab it and use it right now

1. Go here → https://github.com/rod-trent/JunkDrawer/blob/main/JSON_Converter/JSONFormatter.html
2. Click the **Raw** button
3. Save the file as `JSONFormatter.html` (or whatever you want)
4. Double-click it. Done.

Pro tip from me to you: throw it on a USB stick, pin it to your taskbar (Chrome/Edge let you create a shortcut that opens it as its own app), or keep it in your OneDrive/Dropbox. I have copies scattered everywhere because I never know when I’ll need it.

### A quick thank-you

I’ve been genuinely blown away seeing people bookmark it, share it in Slack channels, and even fork it into their own internal toolkits. That’s exactly why I keep the JunkDrawer public – if something I hacked together in 20 minutes helps even one person not want to throw their laptop out the window, it was worth pushing the commit.

So yeah – if this little tool has ever saved your sanity, you’re very welcome. And if you find bugs or want a new feature (JSONPath anyone?), just open an issue. I still maintain it when I’m not buried in Sentinel incidents.

Happy formatting, friends. May your JSON always be valid and your nesting never deeper than you can handle. 😄

– Rod Trent  
(@rodtrent on X/Twitter, BlueSky, Mastodon, and probably a few other places you know)
