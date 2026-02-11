"""
Physiotherapy Exam System - Streamlit Version
Beautiful, fast, and deployable to Streamlit Cloud
"""
import streamlit as st
import json
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Physio Exam System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header */
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    /* Question card */
    .question-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .question-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e293b;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    /* Options */
    .option-button {
        width: 100%;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        background: white;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .option-button:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    /* Feedback */
    .feedback-correct {
        background: #dcfce7;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .feedback-incorrect {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Explanation */
    .explanation {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .explanation-correct {
        border-left: 3px solid #22c55e;
    }
    
    .explanation-incorrect {
        border-left: 3px solid #ef4444;
    }
    
    .explanation-neutral {
        border-left: 3px solid #94a3b8;
    }
    
    /* Timer */
    .timer-warning {
        color: #ef4444;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    .timer-normal {
        color: #1e293b;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    /* Progress bar */
    .progress-text {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    /* Results */
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .result-score {
        font-size: 4rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    
    .result-message {
        font-size: 1.5rem;
        margin-top: 1rem;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'exam_data' not in st.session_state:
    st.session_state.exam_data = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'flagged' not in st.session_state:
    st.session_state.flagged = set()
if 'exam_started' not in st.session_state:
    st.session_state.exam_started = False
if 'exam_finished' not in st.session_state:
    st.session_state.exam_finished = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'duration_minutes' not in st.session_state:
    st.session_state.duration_minutes = 90
if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = {}
if 'exam_history' not in st.session_state:
    st.session_state.exam_history = []

def load_exam_file(uploaded_file):
    """Load exam from uploaded JSON file"""
    try:
        exam_data = json.load(uploaded_file)
        return exam_data
    except Exception as e:
        st.error(f"Error loading exam file: {e}")
        return None

def calculate_score():
    """Calculate exam score"""
    if not st.session_state.exam_data:
        return 0, 0, 0
    
    questions = st.session_state.exam_data['questions']
    total = len(questions)
    flagged_count = len(st.session_state.flagged)
    valid_total = total - flagged_count
    
    correct = 0
    for idx, q in enumerate(questions):
        if idx in st.session_state.flagged:
            continue
        if idx in st.session_state.answers:
            if st.session_state.answers[idx] == q['correct_answer']:
                correct += 1
    
    percentage = (correct / valid_total * 100) if valid_total > 0 else 0
    
    return correct, valid_total, percentage

def get_time_remaining():
    """Get remaining time in seconds"""
    if not st.session_state.start_time:
        return st.session_state.duration_minutes * 60
    
    elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
    remaining = (st.session_state.duration_minutes * 60) - elapsed
    
    return max(0, int(remaining))

def format_time(seconds):
    """Format seconds to MM:SS"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def show_welcome_screen():
    """Display welcome screen"""
    st.markdown('<div class="header-title">🎓 Physiotherapy Exam System</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Practice exams for competitive physiotherapy tests</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📂 Load Exam File")
        uploaded_file = st.file_uploader(
            "Upload your exam JSON file",
            type=['json'],
            help="Load an exam file generated by the Question Generator"
        )
        
        if uploaded_file:
            exam_data = load_exam_file(uploaded_file)
            if exam_data:
                st.session_state.exam_data = exam_data
                st.success(f"✅ Loaded: {exam_data['exam_title']}")
                st.rerun()
    
    # Show statistics if available
    if st.session_state.exam_history:
        st.markdown("---")
        st.markdown("### 📊 Your Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_exams = len(st.session_state.exam_history)
        avg_score = sum(h['percentage'] for h in st.session_state.exam_history) / total_exams
        best_score = max(h['percentage'] for h in st.session_state.exam_history)
        worst_score = min(h['percentage'] for h in st.session_state.exam_history)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_exams}</div>
                <div class="stat-label">Total Exams</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{avg_score:.1f}%</div>
                <div class="stat-label">Average Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{best_score:.1f}%</div>
                <div class="stat-label">Best Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{worst_score:.1f}%</div>
                <div class="stat-label">Worst Score</div>
            </div>
            """, unsafe_allow_html=True)

def show_exam_setup():
    """Display exam setup screen"""
    exam_data = st.session_state.exam_data
    
    st.markdown('<div class="header-title">📝 Exam Setup</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="header-subtitle">{exam_data["exam_title"]}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📋 Question Distribution")
        
        breakdown = exam_data.get('difficulty_breakdown', {})
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value" style="color: #22c55e;">{breakdown.get('easy', 0)}</div>
                <div class="stat-label">Easy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value" style="color: #f59e0b;">{breakdown.get('medium', 0)}</div>
                <div class="stat-label">Medium</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_c:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value" style="color: #ef4444;">{breakdown.get('hard', 0)}</div>
                <div class="stat-label">Hard</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### ⏱️ Exam Duration")
        
        duration = st.slider(
            "Select exam duration (minutes)",
            min_value=30,
            max_value=180,
            value=90,
            step=10,
            help="Set how long you want for this exam"
        )
        
        st.session_state.duration_minutes = duration
        
        st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: #64748b;'>You will have <strong>{duration} minutes</strong> to complete {exam_data['total_questions']} questions</p>", unsafe_allow_html=True)
        
        st.markdown("")
        
        col_x, col_y, col_z = st.columns([1, 1, 1])
        
        with col_y:
            if st.button("🚀 Start Exam", type="primary", use_container_width=True):
                st.session_state.exam_started = True
                st.session_state.start_time = datetime.now()
                st.rerun()

def show_exam_screen():
    """Display exam question screen"""
    exam_data = st.session_state.exam_data
    questions = exam_data['questions']
    current_idx = st.session_state.current_question
    current_q = questions[current_idx]
    
    # Top bar with progress and timer
    col1, col2 = st.columns([3, 1])
    
    with col1:
        progress = (current_idx + 1) / len(questions)
        st.progress(progress)
        st.markdown(f"<div class='progress-text'>Question {current_idx + 1} of {len(questions)}</div>", unsafe_allow_html=True)
    
    with col2:
        remaining = get_time_remaining()
        if remaining == 0:
            st.session_state.exam_finished = True
            st.rerun()
        
        timer_class = "timer-warning" if remaining < 300 else "timer-normal"
        st.markdown(f"<div class='{timer_class}'>⏱️ {format_time(remaining)}</div>", unsafe_allow_html=True)
    
    # Question card
    st.markdown(f"""
    <div class="question-card">
        <div class="question-text">{current_q['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Options
    answered = current_idx in st.session_state.answers
    user_answer = st.session_state.answers.get(current_idx)
    show_explanation = st.session_state.show_explanation.get(current_idx, False)
    
    selected_option = st.radio(
        "Select your answer:",
        options=['A', 'B', 'C', 'D'],
        format_func=lambda x: f"{x}. {current_q['options'][x]}",
        key=f"q_{current_idx}",
        disabled=answered,
        label_visibility="collapsed"
    )
    
    # Buttons
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        if not answered:
            if st.button("🚩 Flag as Irrelevant", use_container_width=True):
                st.session_state.flagged.add(current_idx)
                st.info("Question flagged! It won't count towards your score.")
                time.sleep(1)
                if current_idx < len(questions) - 1:
                    st.session_state.current_question += 1
                    st.rerun()
                else:
                    st.session_state.exam_finished = True
                    st.rerun()
    
    with col2:
        if not answered:
            if st.button("✓ Submit Answer", type="primary", use_container_width=True):
                st.session_state.answers[current_idx] = selected_option
                st.session_state.show_explanation[current_idx] = True
                st.rerun()
    
    with col3:
        if answered:
            if current_idx < len(questions) - 1:
                if st.button("Next →", type="primary", use_container_width=True):
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("Finish Exam", type="primary", use_container_width=True):
                    st.session_state.exam_finished = True
                    st.rerun()
    
    with col4:
        if st.button("⏸️", use_container_width=True, help="Pause and exit"):
            st.session_state.exam_finished = True
            st.rerun()
    
    # Show feedback and explanations
    if show_explanation:
        correct_answer = current_q['correct_answer']
        is_correct = user_answer == correct_answer
        
        if is_correct:
            st.markdown("""
            <div class="feedback-correct">
                <strong style="color: #22c55e; font-size: 1.2rem;">✓ Correct!</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="feedback-incorrect">
                <strong style="color: #ef4444; font-size: 1.2rem;">✗ Incorrect</strong><br>
                <span style="color: #991b1b;">Correct answer: {correct_answer}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📚 Explanations")
        
        for opt in ['A', 'B', 'C', 'D']:
            explanation = current_q['explanations'][opt]
            
            if opt == correct_answer:
                css_class = "explanation-correct"
                icon = "✓"
                color = "#22c55e"
            elif opt == user_answer and opt != correct_answer:
                css_class = "explanation-incorrect"
                icon = "✗"
                color = "#ef4444"
            else:
                css_class = "explanation-neutral"
                icon = "○"
                color = "#64748b"
            
            st.markdown(f"""
            <div class="explanation {css_class}">
                <strong style="color: {color};">{icon} Option {opt}:</strong><br>
                <span style="color: {color};">{explanation}</span>
            </div>
            """, unsafe_allow_html=True)

def show_results_screen():
    """Display results screen"""
    correct, total, percentage = calculate_score()
    
    exam_data = st.session_state.exam_data
    flagged_count = len(st.session_state.flagged)
    
    # Save to history
    result = {
        'date': datetime.now().isoformat(),
        'exam_title': exam_data['exam_title'],
        'correct': correct,
        'total': total,
        'percentage': percentage,
        'flagged': flagged_count
    }
    st.session_state.exam_history.append(result)
    
    st.markdown('<div class="header-title">🎉 Exam Complete!</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="result-card">
            <div style="font-size: 1.2rem; opacity: 0.9;">Your Score</div>
            <div class="result-score">{correct}/{total}</div>
            <div style="font-size: 2rem; font-weight: 600;">{percentage:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        if flagged_count > 0:
            st.info(f"ℹ️ {flagged_count} questions were flagged as irrelevant")
        
        # Performance message
        if percentage >= 80:
            st.success("🌟 Excellent performance!")
        elif percentage >= 60:
            st.success("👍 Good job! Keep practicing!")
        elif percentage >= 40:
            st.warning("📚 Keep studying!")
        else:
            st.info("💪 Don't give up! Practice more!")
        
        st.markdown("")
        
        # Buttons
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🏠 Back to Home", type="primary", use_container_width=True):
                # Reset everything
                st.session_state.exam_data = None
                st.session_state.current_question = 0
                st.session_state.answers = {}
                st.session_state.flagged = set()
                st.session_state.exam_started = False
                st.session_state.exam_finished = False
                st.session_state.start_time = None
                st.session_state.show_explanation = {}
                st.rerun()
        
        with col_b:
            if st.button("📊 View Review", use_container_width=True):
                st.session_state.show_review = True
                st.rerun()

def main():
    """Main application flow"""
    
    # Check if showing review
    if st.session_state.get('show_review', False):
        show_review_screen()
        return
    
    # Route to appropriate screen
    if st.session_state.exam_finished:
        show_results_screen()
    elif st.session_state.exam_started:
        show_exam_screen()
    elif st.session_state.exam_data:
        show_exam_setup()
    else:
        show_welcome_screen()

def show_review_screen():
    """Show detailed review of answers"""
    st.markdown('<div class="header-title">📝 Answer Review</div>', unsafe_allow_html=True)
    
    if st.button("← Back to Results"):
        st.session_state.show_review = False
        st.rerun()
    
    exam_data = st.session_state.exam_data
    questions = exam_data['questions']
    
    for idx, q in enumerate(questions):
        if idx in st.session_state.flagged:
            status = "🚩 Flagged"
            status_color = "#f59e0b"
        elif idx in st.session_state.answers:
            if st.session_state.answers[idx] == q['correct_answer']:
                status = "✓ Correct"
                status_color = "#22c55e"
            else:
                status = "✗ Incorrect"
                status_color = "#ef4444"
        else:
            status = "⊘ Not Answered"
            status_color = "#94a3b8"
        
        with st.expander(f"Question {idx + 1}: {status}", expanded=False):
            st.markdown(f"**{q['question']}**")
            st.markdown("")
            
            for opt in ['A', 'B', 'C', 'D']:
                if opt == q['correct_answer']:
                    st.success(f"✓ {opt}. {q['options'][opt]} (Correct)")
                elif idx in st.session_state.answers and st.session_state.answers[idx] == opt:
                    st.error(f"✗ {opt}. {q['options'][opt]} (Your Answer)")
                else:
                    st.info(f"○ {opt}. {q['options'][opt]}")

if __name__ == "__main__":
    main()
