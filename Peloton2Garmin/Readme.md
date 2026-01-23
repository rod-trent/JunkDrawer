# Peloton to Garmin Sync

A Windows desktop application that seamlessly syncs your Peloton workouts to Garmin Connect with full MFA (Multi-Factor Authentication) support.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

✨ **Headless MFA Support** - Enter your Garmin MFA code directly in the app (no browser required)  
🚴 **Easy Peloton Login** - Simple bearer token authentication  
📊 **Workout Selection** - Choose which workouts to sync  
🔄 **Automatic Conversion** - Converts Peloton workouts to Garmin FIT format  
☁️ **Direct Upload** - Uploads directly to Garmin Connect  
💾 **Session Persistence** - Save tokens to avoid repeated MFA prompts (~1 year)  
🎯 **Duplicate Detection** - Gracefully handles workouts that already exist  
🖥️ **Clean GUI** - User-friendly interface built with tkinter

## Prerequisites

- **Python 3.11+**
- **Windows 10/11** (may work on Mac/Linux with minor modifications)
- **Peloton Account**
- **Garmin Connect Account**

Check out the accompanying blog post: https://rodtrent.substack.com/p/sync-your-peloton-workouts-to-garmin

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/peloton-garmin-sync.git
cd peloton-garmin-sync
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python peloton_garmin_sync_headless_mfa.py
```

## Quick Start Guide

### Step 1: Get Your Peloton Bearer Token

1. Open your web browser and go to [onepeloton.com](https://www.onepeloton.com)
2. Log in to your Peloton account
3. Open Developer Tools (`F12` or `Right-click → Inspect`)
4. Go to the **Network** tab
5. Refresh the page (`F5`)
6. Look for any API request (like `api/user` or `api/me`)
7. Click on that request
8. In the **Headers** section, find `Authorization`
9. Copy everything after `Bearer ` (the long token string)
10. Paste it into the app

### Step 2: Login to Peloton

1. Paste your bearer token in the text box
2. Click **"Login with Token"**
3. ✅ Token is validated and saved

### Step 3: Fetch Your Workouts

1. Click **"Fetch Workouts"**
2. Your recent workouts appear in the list
3. Check the boxes next to workouts you want to sync

### Step 4: Sync to Garmin

1. Click **"Export to Garmin"**
2. Enter your Garmin email and password
3. **If you have MFA enabled:**
   - Check your phone for the 6-digit code
   - Enter it in the dialog that appears
   - Click "Submit Code"
4. Wait for the upload to complete
5. ✅ Done! Check your Garmin Connect

## How MFA Works

The app handles Garmin MFA completely headless (no browser required):

```
1. You click "Export to Garmin"
         ↓
2. App submits your Garmin credentials
         ↓
3. Garmin sends MFA code to your phone
         ↓
4. Dialog appears: "Enter MFA Code"
         ↓
5. You type the 6-digit code
         ↓
6. App submits code to Garmin
         ↓
7. Login successful! Workouts upload
         ↓
8. Session tokens saved (~1 year validity)
```

**Note:** After the first successful MFA login, session tokens are saved. You typically only need to enter your MFA code **once**, not every time you use the app!

## File Structure

```
peloton-garmin-sync/
├── peloton_garmin_sync_headless_mfa.py  # Main application
├── peloton_auth.py                       # Peloton authentication
├── fit_converter.py                      # Workout to FIT conversion
├── settings_manager.py                   # Settings storage
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## Configuration

### Settings Location

User settings are stored in:
```
~/.peloton_garmin_settings.json
```

This includes:
- Peloton bearer token (if you chose to save it)
- Garmin email (if you chose to remember it)
- **Note:** Passwords are NEVER saved

### Garmin Session Tokens

Garmin session tokens are stored in:
```
~/.garminconnect/
```

These tokens:
- Last for approximately **1 year**
- Allow you to skip MFA on subsequent logins
- Are specific to your computer
- Can be safely deleted if you want to force a fresh login

## Troubleshooting

### "ModuleNotFoundError"

**Solution:** Install missing dependencies
```bash
pip install garminconnect garth requests
```

### "429 Too Many Requests" from Garmin

**Cause:** Too many login attempts in a short time  
**Solution:** Wait 15-30 minutes and try again. The rate limit clears automatically.

### "409 Conflict" Error

**This is good news!** It means the workout already exists in Garmin Connect.  
**Solution:** Check your Garmin Connect - the workout is already there.

### MFA Code Not Working

**Solutions:**
- Ensure you're entering the code quickly (they expire)
- Check that you're using the 6-digit code from your phone
- Try generating a new code

### Workouts Not Appearing in Garmin

**Solution:** Wait a few minutes. Garmin processes uploads asynchronously. Check again in 2-5 minutes.

## Limitations

- **Windows Primary** - Designed for Windows (may need adjustments for Mac/Linux)
- **No Auto-Sync** - Manual sync only (not scheduled/automated)
- **Recent Workouts** - Fetches 50 most recent workouts
- **Basic FIT Format** - Creates minimal FIT files (workout data only, no detailed metrics yet)

## Technical Details

### FIT File Format

The app creates minimal but valid FIT files containing:
- Workout timestamp
- Duration
- Calories burned
- Sport type (cycling, running, fitness)
- Session metadata

Future versions may include heart rate, cadence, and power data.

### Authentication Flow

**Peloton:**
- Uses bearer token authentication (OAuth2)
- Token extracted from browser session
- Stored locally for reuse

**Garmin:**
- Uses `garminconnect` library
- OAuth1 and OAuth2 token authentication
- MFA handled via `return_on_mfa` flag
- Session persistence via token storage

## Privacy & Security

✅ **All data stays local** - No third-party servers involved  
✅ **Passwords never stored** - Only bearer tokens and session tokens  
✅ **Direct API communication** - App talks directly to Peloton and Garmin  
✅ **Open source** - All code is visible and auditable

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributions

- Add heart rate, cadence, and power metrics to FIT files
- Create a command-line interface for automation
- Add support for scheduled/automatic syncing
- Improve cross-platform compatibility (Mac/Linux)
- Add unit tests
- Create executable builds for easier distribution

## FAQ

**Q: Do I need MFA enabled on Garmin?**  
A: No, but if you have it enabled, this app handles it properly.

**Q: How often do I need to enter my MFA code?**  
A: Usually just once! Session tokens last ~1 year.

**Q: Can I sync old workouts?**  
A: Yes! The app fetches your 50 most recent workouts. Select any to sync.

**Q: Will this work on Mac/Linux?**  
A: The code should work with minor modifications (paths), but it's currently tested on Windows only.

**Q: Is my data secure?**  
A: Yes. Everything is stored locally. The app communicates directly with Peloton and Garmin APIs using your credentials.

**Q: Can I schedule automatic syncs?**  
A: Not currently. The app requires manual interaction. A CLI version could enable scheduled syncing.

**Q: What if I get a 409 Conflict error?**  
A: This means the workout already exists in Garmin! Check your Garmin Connect - it's already there.

**Q: Does this include heart rate data?**  
A: Not yet. Current version includes basic workout data (duration, calories, sport type). Detailed metrics are planned for future releases.

## Acknowledgments

Built using:
- [garminconnect](https://github.com/cyberjunky/python-garminconnect) - Garmin Connect API wrapper
- [garth](https://github.com/matin/garth) - Garmin authentication library
- Python `tkinter` - GUI framework
- Python `requests` - HTTP library

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial application and is not affiliated with, endorsed by, or connected to Peloton Interactive, Inc. or Garmin Ltd. Use at your own risk.

## Support

If you find this useful, consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs via [Issues](https://github.com/yourusername/peloton-garmin-sync/issues)
- 💡 Suggesting features via [Issues](https://github.com/yourusername/peloton-garmin-sync/issues)
- 🤝 Contributing code via Pull Requests

---

**Made with ❤️ for the Peloton and Garmin community**
