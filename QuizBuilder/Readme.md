# Interactive Quiz Game Platform

A powerful Streamlit application that intelligently generates interactive quiz games from uploaded documents (Excel, Word, JSON, CSV) and tracks player scores with a competitive leaderboard system.

## Features

### 🎯 Core Features
- **Intelligent Quiz Generation**: Automatically parses and generates quiz questions from multiple file formats
- **Multi-Format Support**: Excel (.xlsx, .xls), Word (.docx, .doc), JSON, and CSV files
- **Dual Interface**: Separate Admin and User interfaces for game management and gameplay
- **Score Tracking**: Real-time scoring with accuracy metrics
- **Leaderboard System**: Competitive rankings with player profiles
- **Persistent Storage**: All games and scores saved locally using JSON

### 🎮 Admin Interface
- **Password protected** access (default: `admin123` - change this!)
- Upload documents to create new quiz games
- Custom game titles for each quiz instance
- Preview generated questions before publishing
- View existing games and their statistics
- Access leaderboard data for each game
- Delete games when needed
- Secure logout functionality

### 👤 User Interface
- Browse and select available quiz games
- Create player profiles for score tracking
- Interactive quiz gameplay with multiple question types
- Real-time score and accuracy display
- Answer review after completion
- View leaderboard rankings
- Play again option

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the application**:
```bash
streamlit run quiz_game_app.py
```

3. The app will open in your default browser at `http://localhost:8501`

## Security Configuration

⚠️ **IMPORTANT**: The Admin Panel is password-protected.

**Default Password:** `admin123`

**To change the password:**
1. Open `quiz_game_app.py` in a text editor
2. Find the line: `ADMIN_PASSWORD = "admin123"`
3. Change it to your secure password
4. Save and restart the application

**For detailed security configuration, see SECURITY.md**

## Usage Guide

### For Administrators

1. **Navigate to Admin Panel**: Click the "⚙️ Admin Panel" tab
2. **Login**: Enter the admin password (default: `admin123`) and click **Login**
3. **Create a New Game**:
   - Enter a descriptive game title
   - Upload a source document (Excel, Word, JSON, or CSV)
   - Click "🚀 Generate Quiz Game"
   - Review the generated questions
4. **Manage Games**: View existing games, check statistics, and delete games if needed
5. **Logout**: Click the **🚪 Logout** button when finished

### For Players

1. **Navigate to Play Quiz**: Stay on the "👤 Play Quiz" tab
2. **Select a Game**: Choose from available quiz games in the dropdown
3. **Enter Your Name**: Create your player profile
4. **Play the Quiz**:
   - Read each question carefully
   - Select or type your answer
   - Click "Submit Answer"
   - Review correct/incorrect feedback
5. **View Results**: After completing all questions, see your final score and leaderboard position
6. **Review Answers**: Expand the review section to see all questions and correct answers

## File Format Guidelines

### Excel Files
The app intelligently parses Excel files in multiple ways:

**Option 1: Explicit Q&A Format**
- Column names: `Question`, `Answer`, `Option A`, `Option B`, `Option C`, `Option D`
- Each row contains one question with its answer and optional multiple choice options

**Option 2: Structured Data**
- Any structured data (schedules, agendas, inventories, etc.)
- The app generates contextual questions from the data
- Example: For an agenda, it creates questions about session types, durations, descriptions

### Word Documents
**Option 1: Q&A Pattern**
```
Q: What is the capital of France?
A: Paris

Q: What year did World War II end?
A: 1945
```

**Option 2: Content-Based**
- The app generates questions from document content

### JSON Files
**Option 1: Quiz Format**
```json
[
  {
    "question": "What is 2+2?",
    "answer": "4",
    "options": ["2", "3", "4", "5"]
  }
]
```

**Option 2: Structured Data**
- Any JSON object with key-value pairs
- The app generates questions from the structure

### CSV Files
- Similar to Excel files
- Can be explicit Q&A format or structured data

## Data Storage

The app creates a `quiz_data` directory with the following structure:
```
quiz_data/
├── games.json          # All quiz game data
├── leaderboard.json    # All player scores
└── uploads/            # Uploaded source documents
```

## Question Types

1. **Multiple Choice**: Questions with predefined answer options
2. **Text Input**: Open-ended questions requiring typed answers

## Scoring System

- Each correct answer: +1 point
- Incorrect answers: 0 points
- Final accuracy percentage calculated
- Scores saved to persistent leaderboard
- Rankings based on total score (ties broken by timestamp)

## Customization

### Modifying Question Generation Logic

The `QuizGenerator` class contains methods for each file type:
- `generate_from_excel()`: Excel file parsing
- `generate_from_word()`: Word document parsing
- `generate_from_json()`: JSON file parsing
- `generate_from_csv()`: CSV file parsing

You can customize these methods to adjust how questions are generated for your specific needs.

### Adjusting Question Limits

In `_parse_structured_data()`, modify this line to change the maximum questions per sheet:
```python
if idx >= 10:  # Change this number to generate more/fewer questions
    break
```

## Troubleshooting

### No Questions Generated
- Ensure your file has the correct format
- Check that the file contains sufficient data
- Verify column names match expected patterns (for Q&A format)

### Leaderboard Not Showing
- Make sure you entered a player name
- Complete at least one quiz game
- Check that the `quiz_data` directory has write permissions

### File Upload Fails
- Verify file extension is supported (.xlsx, .xls, .docx, .doc, .json, .csv)
- Check file size (very large files may take longer to process)
- Ensure file is not corrupted

## Advanced Features

### Answer Matching
- Case-insensitive comparison
- Whitespace trimming
- Exact match required for text answers

### Performance Feedback
- 90%+ accuracy: "Outstanding! You're a quiz master!"
- 70-89%: "Great job! Well done!"
- 50-69%: "Good effort! Keep learning!"
- Below 50%: "Keep practicing! You'll improve!"

## Example Use Cases

1. **Training Programs**: Upload training materials to create knowledge checks
2. **Educational Settings**: Convert study guides into interactive quizzes
3. **Conference/Event Apps**: Generate quizzes from event agendas
4. **Team Building**: Create fun trivia games from company information
5. **Product Knowledge**: Test understanding of product specifications

## Future Enhancements (Ideas)

- Timer mode for timed quizzes
- Category-based questions
- Difficulty levels
- Team competitions
- Export results to Excel
- Question bank management
- Image support in questions
- Audio/video question types

## Technical Notes

- Built with Streamlit for rapid development
- Uses pandas for data processing
- python-docx for Word document parsing
- openpyxl for Excel file handling
- JSON for persistent storage
- Session state for game progress tracking

## Contributing

Feel free to modify and extend the application for your specific needs. The modular design makes it easy to add new file format parsers or question generation strategies.

## License

Open source - feel free to use and modify as needed.

## Support

For issues or questions, check the inline code comments or modify the source code to fit your requirements.

# Security Configuration Guide

## Admin Panel Password Protection

The Admin Panel is now password-protected to prevent unauthorized access to quiz game management features.

### Default Password

**Default Admin Password:** `admin123`

⚠️ **IMPORTANT**: Change this password before deploying to production!

### How to Change the Admin Password

1. Open `quiz_game_app.py` in a text editor
2. Find the `CONFIGURATION` section near the top of the file (around line 18)
3. Locate this line:
   ```python
   ADMIN_PASSWORD = "admin123"  # IMPORTANT: Change this password for security!
   ```
4. Change `"admin123"` to your desired password:
   ```python
   ADMIN_PASSWORD = "MySecurePassword123!"
   ```
5. Save the file
6. Restart the Streamlit application

### Password Requirements

- Use a strong password with a mix of:
  - Uppercase letters (A-Z)
  - Lowercase letters (a-z)
  - Numbers (0-9)
  - Special characters (!@#$%^&*)
- Minimum recommended length: 12 characters
- Avoid common words or easily guessable patterns
- Don't use personal information

### Good Password Examples

✅ `QuizMaster2024!Secure`
✅ `AdminP@ssw0rd#Game`
✅ `Str0ng!P@ssword2026`

### Bad Password Examples

❌ `password`
❌ `admin`
❌ `123456`
❌ `quiz`

### Admin Panel Access

1. Navigate to the **⚙️ Admin Panel** tab
2. Enter the admin password
3. Click **Login**
4. If correct, you'll see: "✅ Access granted!"
5. The admin panel features will now be accessible

### Admin Panel Features

Once authenticated, admins can:
- Create new quiz games from uploaded documents
- Preview generated questions
- View existing quiz games and their statistics
- See top scores for each game
- Delete quiz games
- Manage all game content

### Logout

To logout from the admin panel:
1. Click the **🚪 Logout** button in the top-right corner
2. You'll be returned to the login screen
3. Session expires when you close the browser or navigate away

### Session Management

- Authentication is stored in Streamlit's session state
- Each browser tab/window requires separate authentication
- Closing the browser ends the session
- No persistent authentication across sessions (must login each time)

### Security Best Practices

1. **Change the Default Password Immediately**
   - The default `admin123` is publicly known
   - Change it before allowing any external access

2. **Keep Your Password Secret**
   - Don't share your admin password
   - Don't commit it to public repositories
   - Don't include it in screenshots or documentation

3. **Use Environment Variables (Advanced)**
   For production deployments, consider using environment variables:
   ```python
   import os
   ADMIN_PASSWORD = os.getenv("QUIZ_ADMIN_PASSWORD", "admin123")
   ```
   Then set the environment variable before running:
   ```bash
   export QUIZ_ADMIN_PASSWORD="YourSecurePassword"
   streamlit run quiz_game_app.py
   ```

4. **Regular Password Changes**
   - Change the admin password periodically
   - Change immediately if you suspect it's been compromised

5. **Monitor Access**
   - Check the Admin Panel regularly for unauthorized changes
   - Review created games and leaderboard data

### Multiple Admin Passwords (Advanced)

To support multiple admin users with different passwords, modify the code:

```python
# At the top of the file
ADMIN_PASSWORDS = [
    "admin123",           # Admin 1
    "manager456",         # Admin 2
    "supervisor789"       # Admin 3
]

# In the admin_interface function
if password_input in ADMIN_PASSWORDS:
    st.session_state.admin_authenticated = True
    st.success("✅ Access granted!")
    st.rerun()
```

### Troubleshooting

**I forgot my admin password!**
- Edit `quiz_game_app.py` and change the `ADMIN_PASSWORD` value
- Restart the application
- You can now login with the new password

**The password isn't working!**
- Passwords are case-sensitive (check Caps Lock)
- Make sure there are no extra spaces before/after
- Verify you edited the correct file and restarted the app
- Check that your changes were saved properly

**I want to disable password protection**
- Not recommended for production
- For testing, you can comment out the authentication check:
  ```python
  # if not st.session_state.admin_authenticated:
  #     # ... password check code ...
  #     return
  st.session_state.admin_authenticated = True  # Auto-authenticate for testing
  ```

### Additional Security Considerations

1. **HTTPS/SSL**: When deploying publicly, use HTTPS to encrypt password transmission
2. **Access Logs**: Consider adding logging for admin access attempts
3. **Rate Limiting**: For production, implement rate limiting on login attempts
4. **Two-Factor Authentication**: For high-security needs, consider implementing 2FA
5. **IP Whitelisting**: Restrict admin access to specific IP addresses if possible

### Support

For questions about security configuration, refer to:
- Main README.md for general application documentation
- QUICKSTART.md for basic setup instructions
- This document for security-specific guidance

## Summary

✅ Default password: `admin123`
✅ Change in: `ADMIN_PASSWORD` variable in `quiz_game_app.py`
✅ Location: Top of file in CONFIGURATION section
✅ Restart required: Yes, after changing password
✅ Session-based: Authentication doesn't persist across sessions

**Remember: Security is only as strong as your weakest password. Change the default immediately!**

