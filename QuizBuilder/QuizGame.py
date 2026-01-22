"""
Interactive Quiz Game Application
A Streamlit app that intelligently generates quizzes from uploaded documents
and tracks player scores with a leaderboard system.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
import random
from typing import List, Dict, Any
import docx  # python-docx for Word files
import openpyxl

# ============================================================================
# CONFIGURATION - Change these settings as needed
# ============================================================================
ADMIN_PASSWORD = "admin123"  # IMPORTANT: Change this password for security!

# ============================================================================
# File paths and directories
# ============================================================================
DATA_DIR = Path("quiz_data")
GAMES_FILE = DATA_DIR / "games.json"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"
UPLOADS_DIR = DATA_DIR / "uploads"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)


class QuizGenerator:
    """Intelligent quiz generation from various file formats"""
    
    @staticmethod
    def generate_from_excel(file_path: str) -> List[Dict[str, Any]]:
        """Generate quiz questions from Excel files"""
        questions = []
        excel_file = pd.ExcelFile(file_path)
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Skip empty sheets
            if df.empty:
                continue
            
            # Strategy 1: If there are clear question/answer columns
            if any('question' in col.lower() for col in df.columns):
                questions.extend(QuizGenerator._parse_qa_format(df))
            
            # Strategy 2: Generate questions from structured data (like agenda)
            else:
                questions.extend(QuizGenerator._parse_structured_data(df, sheet_name))
        
        return questions
    
    @staticmethod
    def _parse_qa_format(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Parse explicit question-answer format"""
        questions = []
        
        # Find question and answer columns
        q_col = next((col for col in df.columns if 'question' in col.lower()), None)
        a_col = next((col for col in df.columns if 'answer' in col.lower()), None)
        
        if not q_col or not a_col:
            return questions
        
        # Look for options columns (A, B, C, D or Option1, Option2, etc.)
        option_cols = [col for col in df.columns if 'option' in col.lower() or col in ['A', 'B', 'C', 'D']]
        
        for idx, row in df.iterrows():
            if pd.notna(row[q_col]) and pd.notna(row[a_col]):
                correct_answer = str(row[a_col])
                
                # Get options if provided
                if option_cols:
                    options = [str(row[col]) for col in option_cols if pd.notna(row[col])]
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_options = []
                    for opt in options:
                        if opt not in seen:
                            seen.add(opt)
                            unique_options.append(opt)
                    
                    # Ensure we have at least 4 unique options including the correct answer
                    if len(unique_options) >= 4:
                        # Make sure correct answer is in options
                        if correct_answer not in unique_options:
                            unique_options = [correct_answer] + unique_options[:3]
                        
                        random.shuffle(unique_options)
                        
                        questions.append({
                            'question': str(row[q_col]),
                            'correct_answer': correct_answer,
                            'options': unique_options[:4],
                            'type': 'multiple_choice'
                        })
                else:
                    # Generate options from other answers in the dataset
                    other_answers = df[df.index != idx][a_col].dropna().unique().tolist()
                    
                    if len(other_answers) >= 3:
                        wrong_answers = random.sample(other_answers, min(3, len(other_answers)))
                        # Ensure no duplicates
                        wrong_answers = [str(ans) for ans in wrong_answers if str(ans) != correct_answer][:3]
                        
                        if len(wrong_answers) == 3:
                            all_options = [correct_answer] + wrong_answers
                            random.shuffle(all_options)
                            
                            questions.append({
                                'question': str(row[q_col]),
                                'correct_answer': correct_answer,
                                'options': all_options,
                                'type': 'multiple_choice'
                            })
        
        return questions
    
    @staticmethod
    def _parse_structured_data(df: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """Generate questions from structured data (like schedules, agendas, etc.)"""
        questions = []
        
        # Get non-null columns with meaningful data
        valid_cols = [col for col in df.columns if df[col].notna().sum() > 0]
        
        if len(valid_cols) < 2:
            return questions
        
        # Generate different types of questions
        for idx, row in df.iterrows():
            if idx >= 10:  # Limit questions per sheet
                break
            
            # Skip rows with too many nulls
            if row.isna().sum() > len(valid_cols) * 0.5:
                continue
            
            # Question Type 1: "What is the [column] of [identifier]?" - Multiple Choice
            if 'TITLE' in valid_cols and 'DESCRIPTION' in valid_cols:
                if pd.notna(row['TITLE']) and pd.notna(row['DESCRIPTION']):
                    # Get other unique descriptions as wrong answers
                    other_descriptions = df[df.index != idx]['DESCRIPTION'].dropna().unique().tolist()
                    if len(other_descriptions) >= 3:
                        wrong_answers = random.sample(other_descriptions, min(3, len(other_descriptions)))
                        # Ensure no duplicates
                        wrong_answers = [str(ans) for ans in wrong_answers if str(ans) != str(row['DESCRIPTION'])][:3]
                        
                        if len(wrong_answers) == 3:
                            all_options = [str(row['DESCRIPTION'])] + wrong_answers
                            random.shuffle(all_options)
                            
                            questions.append({
                                'question': f"What is the description of '{row['TITLE']}'?",
                                'correct_answer': str(row['DESCRIPTION']),
                                'options': all_options,
                                'type': 'multiple_choice',
                                'source': sheet_name
                            })
            
            # Question Type 2: Multiple choice from categorical data
            if 'SESSION_TYPE' in valid_cols and 'TITLE' in valid_cols:
                if pd.notna(row['SESSION_TYPE']) and pd.notna(row['TITLE']):
                    # Get other session types as wrong answers
                    other_types = df[df.index != idx]['SESSION_TYPE'].dropna().unique().tolist()
                    if len(other_types) >= 3:
                        wrong_answers = random.sample(other_types, min(3, len(other_types)))
                        # Ensure no duplicates and not same as correct answer
                        wrong_answers = [str(ans) for ans in wrong_answers if str(ans) != str(row['SESSION_TYPE'])][:3]
                        
                        if len(wrong_answers) == 3:
                            all_options = [str(row['SESSION_TYPE'])] + wrong_answers
                            random.shuffle(all_options)
                            
                            questions.append({
                                'question': f"What type of session is '{row['TITLE']}'?",
                                'correct_answer': str(row['SESSION_TYPE']),
                                'options': all_options,
                                'type': 'multiple_choice',
                                'source': sheet_name
                            })
            
            # Question Type 3: Duration/Numeric questions with plausible alternatives
            if 'DURATION' in valid_cols and 'TITLE' in valid_cols:
                if pd.notna(row['DURATION']) and pd.notna(row['TITLE']):
                    # Get other durations as options
                    other_durations = df[df.index != idx]['DURATION'].dropna().unique().tolist()
                    if len(other_durations) >= 3:
                        wrong_answers = random.sample(other_durations, min(3, len(other_durations)))
                        # Ensure no duplicates
                        wrong_answers = [str(ans) for ans in wrong_answers if str(ans) != str(row['DURATION'])][:3]
                        
                        if len(wrong_answers) == 3:
                            all_options = [str(row['DURATION'])] + wrong_answers
                            random.shuffle(all_options)
                            
                            questions.append({
                                'question': f"What is the duration of '{row['TITLE']}'?",
                                'correct_answer': str(row['DURATION']),
                                'options': all_options,
                                'type': 'multiple_choice',
                                'source': sheet_name
                            })
            
            # Question Type 4: Speaker/Person questions
            if 'SPEAKERS' in valid_cols and 'TITLE' in valid_cols:
                if pd.notna(row['SPEAKERS']) and pd.notna(row['TITLE']):
                    # Get other speakers as options
                    other_speakers = df[df.index != idx]['SPEAKERS'].dropna().unique().tolist()
                    if len(other_speakers) >= 3:
                        wrong_answers = random.sample(other_speakers, min(3, len(other_speakers)))
                        # Ensure no duplicates
                        wrong_answers = [str(ans) for ans in wrong_answers if str(ans) != str(row['SPEAKERS'])][:3]
                        
                        if len(wrong_answers) == 3:
                            all_options = [str(row['SPEAKERS'])] + wrong_answers
                            random.shuffle(all_options)
                            
                            questions.append({
                                'question': f"Who is speaking at '{row['TITLE']}'?",
                                'correct_answer': str(row['SPEAKERS']),
                                'options': all_options,
                                'type': 'multiple_choice',
                                'source': sheet_name
                            })
            
            # Question Type 5: Room/Location questions
            if 'ROOM' in valid_cols and 'TITLE' in valid_cols:
                if pd.notna(row['ROOM']) and pd.notna(row['TITLE']):
                    # Get other rooms as options
                    other_rooms = df[df.index != idx]['ROOM'].dropna().unique().tolist()
                    if len(other_rooms) >= 3:
                        wrong_answers = random.sample(other_rooms, min(3, len(other_rooms)))
                        # Ensure no duplicates
                        wrong_answers = [str(ans) for ans in wrong_answers if str(ans) != str(row['ROOM'])][:3]
                        
                        if len(wrong_answers) == 3:
                            all_options = [str(row['ROOM'])] + wrong_answers
                            random.shuffle(all_options)
                            
                            questions.append({
                                'question': f"In which room is '{row['TITLE']}' held?",
                                'correct_answer': str(row['ROOM']),
                                'options': all_options,
                                'type': 'multiple_choice',
                                'source': sheet_name
                            })
        
        return questions
    
    @staticmethod
    def generate_from_word(file_path: str) -> List[Dict[str, Any]]:
        """Generate quiz questions from Word documents"""
        questions = []
        doc = docx.Document(file_path)
        
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        
        # Look for Q&A patterns
        qa_pairs = []
        for i, para in enumerate(paragraphs):
            if para.lower().startswith(('q:', 'question:', 'q.', 'question ')):
                question_text = para.split(':', 1)[-1].strip()
                
                # Look for answer in next paragraph
                if i + 1 < len(paragraphs):
                    next_para = paragraphs[i + 1]
                    if next_para.lower().startswith(('a:', 'answer:', 'a.', 'answer ')):
                        answer_text = next_para.split(':', 1)[-1].strip()
                        qa_pairs.append({
                            'question': question_text,
                            'answer': answer_text
                        })
        
        # Convert to multiple choice with unique options
        if qa_pairs:
            for qa in qa_pairs:
                # Use other answers as wrong options
                other_answers = [pair['answer'] for pair in qa_pairs if pair['answer'] != qa['answer']]
                
                if len(other_answers) >= 3:
                    wrong_answers = random.sample(other_answers, 3)
                    all_options = [qa['answer']] + wrong_answers
                    random.shuffle(all_options)
                    
                    questions.append({
                        'question': qa['question'],
                        'correct_answer': qa['answer'],
                        'options': all_options,
                        'type': 'multiple_choice'
                    })
                elif len(other_answers) > 0:
                    # Generate plausible fake answers if we don't have enough
                    wrong_answers = other_answers[:3]
                    # Add generic wrong answers if needed
                    generic_wrongs = ["None of the above", "Not specified", "Unknown"]
                    while len(wrong_answers) < 3:
                        for gw in generic_wrongs:
                            if gw not in wrong_answers and gw != qa['answer']:
                                wrong_answers.append(gw)
                                if len(wrong_answers) == 3:
                                    break
                    
                    all_options = [qa['answer']] + wrong_answers[:3]
                    random.shuffle(all_options)
                    
                    questions.append({
                        'question': qa['question'],
                        'correct_answer': qa['answer'],
                        'options': all_options,
                        'type': 'multiple_choice'
                    })
        
        # If no Q&A pattern found, generate from content
        if not questions and len(paragraphs) > 5:
            for i in range(0, min(len(paragraphs), 10), 2):
                if i + 1 < len(paragraphs) and len(paragraphs[i]) > 10:
                    # Create questions about paragraph content
                    other_paras = [p for j, p in enumerate(paragraphs) if j != i and len(p) > 10]
                    
                    if len(other_paras) >= 3:
                        wrong_answers = random.sample(other_paras[:20], min(3, len(other_paras)))
                        all_options = [paragraphs[i]] + wrong_answers
                        random.shuffle(all_options)
                        
                        questions.append({
                            'question': f"Which statement comes from the document?",
                            'correct_answer': paragraphs[i],
                            'options': all_options,
                            'type': 'multiple_choice'
                        })
        
        return questions
    
    @staticmethod
    def generate_from_json(file_path: str) -> List[Dict[str, Any]]:
        """Generate quiz questions from JSON files"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        questions = []
        
        # If it's already a quiz format
        if isinstance(data, list) and all(isinstance(q, dict) for q in data):
            for item in data:
                if 'question' in item and 'answer' in item:
                    options = item.get('options', [])
                    
                    # Ensure we have multiple choice with unique options
                    if options and len(options) >= 4:
                        # Remove duplicates
                        unique_options = list(dict.fromkeys([str(opt) for opt in options]))
                        if len(unique_options) >= 4:
                            questions.append({
                                'question': item['question'],
                                'correct_answer': str(item['answer']),
                                'options': unique_options[:4],
                                'type': 'multiple_choice'
                            })
                    else:
                        # Generate options from other answers
                        other_answers = [q['answer'] for q in data if q.get('answer') and q['answer'] != item['answer']]
                        if len(other_answers) >= 3:
                            wrong_answers = random.sample(other_answers, 3)
                            all_options = [str(item['answer'])] + [str(ans) for ans in wrong_answers]
                            # Remove duplicates while preserving order
                            seen = set()
                            unique_options = []
                            for opt in all_options:
                                if opt not in seen:
                                    seen.add(opt)
                                    unique_options.append(opt)
                            
                            if len(unique_options) >= 4:
                                random.shuffle(unique_options)
                                questions.append({
                                    'question': item['question'],
                                    'correct_answer': str(item['answer']),
                                    'options': unique_options[:4],
                                    'type': 'multiple_choice'
                                })
        
        # Generate from structured JSON
        elif isinstance(data, dict):
            items = list(data.items())
            for key, value in items:
                if isinstance(value, (str, int, float)):
                    # Get other values as wrong options
                    other_values = [str(v) for k, v in items if k != key and isinstance(v, (str, int, float))]
                    
                    if len(other_values) >= 3:
                        wrong_answers = random.sample(other_values, 3)
                        # Ensure no duplicates
                        all_options = [str(value)] + [ans for ans in wrong_answers if str(ans) != str(value)][:3]
                        
                        if len(all_options) >= 4:
                            random.shuffle(all_options)
                            questions.append({
                                'question': f"What is the value of '{key}'?",
                                'correct_answer': str(value),
                                'options': all_options[:4],
                                'type': 'multiple_choice'
                            })
        
        return questions
    
    @staticmethod
    def generate_from_csv(file_path: str) -> List[Dict[str, Any]]:
        """Generate quiz questions from CSV files"""
        df = pd.read_csv(file_path)
        return QuizGenerator._parse_structured_data(df, "CSV Data")


class GameManager:
    """Manage quiz games and their data"""
    
    @staticmethod
    def load_games() -> Dict[str, Any]:
        """Load all games from storage"""
        if GAMES_FILE.exists():
            with open(GAMES_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_games(games: Dict[str, Any]):
        """Save games to storage"""
        with open(GAMES_FILE, 'w') as f:
            json.dump(games, f, indent=2)
    
    @staticmethod
    def create_game(title: str, file_path: str, file_type: str) -> Dict[str, Any]:
        """Create a new quiz game from uploaded file"""
        generator = QuizGenerator()
        
        # Generate questions based on file type
        if file_type in ['xlsx', 'xls']:
            questions = generator.generate_from_excel(file_path)
        elif file_type in ['docx', 'doc']:
            questions = generator.generate_from_word(file_path)
        elif file_type == 'json':
            questions = generator.generate_from_json(file_path)
        elif file_type == 'csv':
            questions = generator.generate_from_csv(file_path)
        else:
            questions = []
        
        game_id = f"game_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        game = {
            'id': game_id,
            'title': title,
            'created_at': datetime.now().isoformat(),
            'file_type': file_type,
            'questions': questions,
            'total_questions': len(questions)
        }
        
        return game


class LeaderboardManager:
    """Manage player scores and leaderboard"""
    
    @staticmethod
    def load_leaderboard() -> Dict[str, List[Dict[str, Any]]]:
        """Load leaderboard data"""
        if LEADERBOARD_FILE.exists():
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_leaderboard(leaderboard: Dict[str, List[Dict[str, Any]]]):
        """Save leaderboard data"""
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(leaderboard, f, indent=2)
    
    @staticmethod
    def add_score(game_id: str, player_name: str, score: int, total: int):
        """Add a score to the leaderboard"""
        leaderboard = LeaderboardManager.load_leaderboard()
        
        if game_id not in leaderboard:
            leaderboard[game_id] = []
        
        leaderboard[game_id].append({
            'player': player_name,
            'score': score,
            'total': total,
            'percentage': round((score / total * 100), 2) if total > 0 else 0,
            'timestamp': datetime.now().isoformat()
        })
        
        # Sort by score (descending)
        leaderboard[game_id].sort(key=lambda x: x['score'], reverse=True)
        
        LeaderboardManager.save_leaderboard(leaderboard)
    
    @staticmethod
    def get_top_scores(game_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top scores for a game"""
        leaderboard = LeaderboardManager.load_leaderboard()
        return leaderboard.get(game_id, [])[:limit]


def admin_interface():
    """Admin interface for creating and managing quiz games"""
    st.header("🎮 Quiz Game Administration")
    
    # Check if admin is authenticated
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.info("🔒 Admin access is password protected.")
        
        password_input = st.text_input("Enter Admin Password:", type="password", key="admin_password")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Login", type="primary"):
                if password_input == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.success("✅ Access granted!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Access denied.")
        
        with col2:
            if st.button("Back to Quiz"):
                st.info("Returning to Play Quiz tab...")
        
        st.divider()
        st.markdown("""
        **Security Note:** 
        - Default password is `admin123`
        - To change the password, edit the `ADMIN_PASSWORD` variable at the top of the code
        - Keep your password secure and don't share it publicly
        """)
        return
    
    # Logout button for authenticated admins
    col1, col2 = st.columns([5, 1])
    with col1:
        st.success("🔓 Authenticated as Admin")
    with col2:
        if st.button("🚪 Logout", key="admin_logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    st.divider()
    
    # Create new game section
    st.subheader("Create New Quiz Game")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        game_title = st.text_input("Game Title", placeholder="Enter a descriptive title for your quiz")
    
    uploaded_file = st.file_uploader(
        "Upload Source Document",
        type=['xlsx', 'xls', 'docx', 'doc', 'json', 'csv'],
        help="Upload Excel, Word, JSON, or CSV files to generate quiz questions"
    )
    
    if uploaded_file and game_title:
        if st.button("🚀 Generate Quiz Game", type="primary"):
            with st.spinner("Analyzing document and generating questions..."):
                try:
                    # Save uploaded file
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    save_path = UPLOADS_DIR / f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
                    
                    with open(save_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Create game
                    game = GameManager.create_game(game_title, str(save_path), file_extension)
                    
                    if game['total_questions'] == 0:
                        st.error("❌ No questions could be generated from this file. Please check the file format and try again.")
                        st.info("💡 Tip: For Excel files, include columns like 'Question' and 'Answer', or use structured data.")
                    else:
                        # Save game
                        games = GameManager.load_games()
                        games[game['id']] = game
                        GameManager.save_games(games)
                        
                        st.success(f"✅ Quiz game created successfully with {game['total_questions']} questions!")
                        st.info("💡 Switch to the 'Play Quiz' tab to start playing!")
                        
                        # Preview questions
                        st.subheader("Question Preview")
                        for i, q in enumerate(game['questions'][:5], 1):
                            with st.expander(f"Question {i}: {q['question'][:50]}..."):
                                st.write(f"**Question:** {q['question']}")
                                st.write(f"**Type:** {q['type']}")
                                st.write(f"**Answer:** {q['correct_answer']}")
                                if q.get('options'):
                                    st.write(f"**Options:** {', '.join(q['options'])}")
                        
                        if game['total_questions'] > 5:
                            st.info(f"Showing 5 of {game['total_questions']} questions")
                        
                        # Force a rerun to update the app state
                        st.session_state['game_created'] = True
                        
                except Exception as e:
                    st.error(f"❌ Error creating game: {str(e)}")
                    st.info("Please check your file format and try again.")
    
    # Existing games section
    st.subheader("Existing Quiz Games")
    games = GameManager.load_games()
    
    if games:
        for game_id, game in games.items():
            with st.expander(f"📝 {game['title']} ({game['total_questions']} questions)"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Questions", game['total_questions'])
                col2.metric("File Type", game['file_type'].upper())
                col3.metric("Created", game['created_at'][:10])
                
                # Show leaderboard preview
                top_scores = LeaderboardManager.get_top_scores(game_id, 3)
                if top_scores:
                    st.write("**Top 3 Scores:**")
                    for i, score in enumerate(top_scores, 1):
                        st.write(f"{i}. {score['player']}: {score['score']}/{score['total']} ({score['percentage']}%)")
                
                if st.button(f"Delete Game", key=f"del_{game_id}"):
                    del games[game_id]
                    GameManager.save_games(games)
                    st.rerun()
    else:
        st.info("No quiz games created yet. Upload a document to get started!")


def user_interface():
    """User interface for playing quiz games"""
    st.header("🎯 Play Quiz Game")
    
    # Show success message if coming from game creation
    if st.session_state.get('game_created'):
        st.success("🎉 New game available! Select it from the dropdown below.")
        st.session_state['game_created'] = False
    
    # Add refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Games"):
            st.rerun()
    
    games = GameManager.load_games()
    
    if not games:
        st.warning("No quiz games available. Ask an administrator to create one!")
        st.info("👉 Go to the **Admin Panel** tab to create your first quiz game!")
        return
    
    # Game selection
    game_titles = {game['title']: game_id for game_id, game in games.items()}
    selected_title = st.selectbox("Select a Quiz Game", options=list(game_titles.keys()))
    selected_game_id = game_titles[selected_title]
    selected_game = games[selected_game_id]
    
    # Player name
    if 'player_name' not in st.session_state:
        st.session_state.player_name = ""
    
    player_name = st.text_input("Enter Your Name", value=st.session_state.player_name, placeholder="Your name for the leaderboard")
    
    if player_name:
        st.session_state.player_name = player_name
        
        # Initialize game state
        if 'current_game_id' not in st.session_state or st.session_state.current_game_id != selected_game_id:
            st.session_state.current_game_id = selected_game_id
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answers = []
            st.session_state.game_complete = False
            st.session_state['score_saved'] = False
        
        # Display game info
        col1, col2, col3 = st.columns(3)
        col1.metric("Question", f"{st.session_state.current_question + 1}/{selected_game['total_questions']}")
        col2.metric("Score", st.session_state.score)
        col3.metric("Accuracy", f"{round(st.session_state.score / max(st.session_state.current_question, 1) * 100, 1)}%")
        
        # Game play
        if not st.session_state.game_complete:
            if st.session_state.current_question < selected_game['total_questions']:
                current_q = selected_game['questions'][st.session_state.current_question]
                
                st.subheader(f"Question {st.session_state.current_question + 1}")
                st.write(current_q['question'])
                
                # All questions are now multiple choice
                if current_q.get('options') and len(current_q['options']) >= 2:
                    user_answer = st.radio(
                        "Select your answer:", 
                        current_q['options'], 
                        key=f"q_{st.session_state.current_question}",
                        index=None
                    )
                else:
                    st.error("This question doesn't have valid multiple choice options.")
                    user_answer = None
                
                if user_answer and st.button("Submit Answer", type="primary"):
                    # Check answer
                    is_correct = user_answer.strip().lower() == current_q['correct_answer'].strip().lower()
                    
                    if is_correct:
                        st.session_state.score += 1
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The correct answer is: {current_q['correct_answer']}")
                    
                    st.session_state.answers.append({
                        'question': current_q['question'],
                        'user_answer': user_answer,
                        'correct_answer': current_q['correct_answer'],
                        'is_correct': is_correct
                    })
                    
                    st.session_state.current_question += 1
                    
                    if st.session_state.current_question >= selected_game['total_questions']:
                        st.session_state.game_complete = True
                    
                    # Rerun to refresh the page and show updated leaderboard
                    st.rerun()
            
        else:
            # Game complete
            st.balloons()
            st.success("🎉 Quiz Complete!")
            
            final_score = st.session_state.score
            total_questions = selected_game['total_questions']
            percentage = round((final_score / total_questions * 100), 2)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Final Score", f"{final_score}/{total_questions}")
            col2.metric("Accuracy", f"{percentage}%")
            
            # Performance message
            if percentage >= 90:
                st.success("🏆 Outstanding! You're a quiz master!")
            elif percentage >= 70:
                st.info("👍 Great job! Well done!")
            elif percentage >= 50:
                st.warning("📚 Good effort! Keep learning!")
            else:
                st.error("💪 Keep practicing! You'll improve!")
            
            # Save to leaderboard (only once)
            if not st.session_state.get('score_saved'):
                LeaderboardManager.add_score(selected_game_id, player_name, final_score, total_questions)
                st.session_state['score_saved'] = True
                st.session_state['leaderboard_updated'] = True
            
            # Show review
            with st.expander("📋 Review Your Answers"):
                for i, ans in enumerate(st.session_state.answers, 1):
                    icon = "✅" if ans['is_correct'] else "❌"
                    st.write(f"{icon} **Q{i}:** {ans['question']}")
                    st.write(f"   Your answer: {ans['user_answer']}")
                    if not ans['is_correct']:
                        st.write(f"   Correct answer: {ans['correct_answer']}")
                    st.divider()
            
            if st.button("Play Again"):
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.answers = []
                st.session_state.game_complete = False
                st.session_state['leaderboard_updated'] = False
                st.session_state['score_saved'] = False
                st.rerun()
    
    # Leaderboard section - Always visible
    st.divider()
    st.subheader("🏆 Live Leaderboard")
    
    # Add refresh button for leaderboard
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.get('leaderboard_updated'):
            st.success("✅ Your score has been added to the leaderboard!")
            st.session_state['leaderboard_updated'] = False
    with col2:
        if st.button("🔄 Refresh", key="refresh_leaderboard"):
            st.rerun()
    
    top_scores = LeaderboardManager.get_top_scores(selected_game_id, 10)
    
    if top_scores:
        leaderboard_df = pd.DataFrame(top_scores)
        leaderboard_df['rank'] = range(1, len(leaderboard_df) + 1)
        leaderboard_df = leaderboard_df[['rank', 'player', 'score', 'total', 'percentage']]
        leaderboard_df.columns = ['Rank', 'Player', 'Score', 'Total', 'Accuracy %']
        
        # Highlight current player
        def highlight_current_player(row):
            if row['Player'] == player_name:
                return ['background-color: #ffffcc; font-weight: bold'] * len(row)
            return [''] * len(row)
        
        try:
            styled_df = leaderboard_df.style.apply(highlight_current_player, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        except:
            # Fallback if styling fails
            st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
        
        # Show current player's rank if they're on the board
        player_scores = [s for s in top_scores if s['player'] == player_name]
        if player_scores:
            best_rank = next((i+1 for i, s in enumerate(top_scores) if s['player'] == player_name), None)
            if best_rank:
                st.info(f"🎯 Your best rank: #{best_rank} with {player_scores[0]['score']}/{player_scores[0]['total']} points")
    else:
        st.info("No scores yet. Complete the quiz to be the first on the leaderboard!")


def main():
    """Main application"""
    st.set_page_config(
        page_title="Interactive Quiz Game",
        page_icon="🎮",
        layout="wide"
    )
    
    st.title("🎮 Interactive Quiz Game Platform")
    st.markdown("Build intelligent quizzes from documents and compete on the leaderboard!")
    
    # Tab navigation
    tab1, tab2 = st.tabs(["👤 Play Quiz", "⚙️ Admin Panel"])
    
    with tab1:
        user_interface()
    
    with tab2:
        admin_interface()
    
    # Footer
    st.divider()
    st.caption("Quiz Game Platform | Upload documents to automatically generate engaging quizzes")


if __name__ == "__main__":
    main()
