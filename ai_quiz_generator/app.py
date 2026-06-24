"""
AI Quiz Generator
=================
A premium Streamlit application that transforms PowerPoint presentations
into intelligent interactive quizzes with AI-powered question generation,
scoring, and feedback.

Author: AI Quiz Generator Team
Version: 1.0.0
"""

import json
import os
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config MUST be the first Streamlit command
st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import utility modules
from utils.ppt_parser import extract_ppt_content, format_file_size, get_slide_preview, PPTParserError
from utils.quiz_generator import QuizGenerator, QuizGeneratorError
from utils.scoring import QuizScorer
from utils.helpers import (
    init_session_state,
    set_page,
    load_css,
    inject_particles,
    inject_confetti,
    render_svg_logo,
    render_metric_card,
    render_processing_animation,
    format_time,
    get_timer_duration,
    validate_api_key,
    get_app_info,
    create_sample_quiz
)

# ============================================
# INITIALIZATION
# ============================================

init_session_state()
load_css()

# ============================================
# SIDEBAR CONFIGURATION
# ============================================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">🧠</div>
        <div style="font-weight:700;font-size:1.2rem;color:var(--text);">AI Quiz Generator</div>
        <div style="color:var(--text-secondary);font-size:0.8rem;">v1.0.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr class='premium-divider'>", unsafe_allow_html=True)
    
    # API Configuration
    st.markdown("""
    <div style="font-weight:600;color:var(--text);margin-bottom:0.5rem;">
        ⚙️ API Configuration
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input(
        "API Key (optional)",
        type="password",
        placeholder="sk-...",
        help="Enter your OpenAI or DeepSeek API key for AI-powered quiz generation. Leave empty for mock generation.",
        value=st.session_state.get("api_key", "")
    )
    
    api_url = st.text_input(
        "API URL (optional)",
        placeholder="https://api.openai.com/v1",
        help="Custom API endpoint URL. Leave empty for default OpenAI endpoint.",
        value=st.session_state.get("api_url", "")
    )
    
    model = st.text_input(
        "Model (optional)",
        placeholder="gpt-3.5-turbo",
        help="Model name to use for generation.",
        value="gpt-3.5-turbo"
    )
    
    use_llm = st.checkbox(
        "Use AI Generation",
        value=bool(api_key),
        help="Enable AI-powered question generation using your API key."
    )
    
    # Update session state
    st.session_state.api_key = api_key
    st.session_state.api_url = api_url if api_url else None
    st.session_state.use_llm = use_llm and bool(api_key)
    
    st.markdown("<hr class='premium-divider'>", unsafe_allow_html=True)
    
    # Navigation
    st.markdown("""
    <div style="font-weight:600;color:var(--text);margin-bottom:0.5rem;">
        🧭 Navigation
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Home", use_container_width=True):
        set_page("landing")
    
    if st.session_state.quiz_started and not st.session_state.quiz_completed:
        if st.button("📝 Resume Quiz", use_container_width=True):
            set_page("quiz")
    
    if st.session_state.quiz_completed:
        if st.button("📊 View Results", use_container_width=True):
            set_page("results")
    
    if st.button("🔄 Reset Application", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("<hr class='premium-divider'>", unsafe_allow_html=True)
    
    # App Info
    app_info = get_app_info()
    st.markdown(f"""
    <div style="text-align:center;color:var(--text-muted);font-size:0.75rem;padding:1rem 0;">
        {app_info['name']} v{app_info['version']}<br>
        © {app_info['year']} {app_info['author']}
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN APP ROUTER
# ============================================

def main():
    """Main application router - directs to the appropriate page."""
    
    # Inject background particles
    inject_particles()
    
    # Route to the correct page
    page = st.session_state.page
    
    if page == "landing":
        render_landing_page()
    elif page == "upload":
        render_upload_page()
    elif page == "configure":
        render_configuration_page()
    elif page == "processing":
        render_processing_page()
    elif page == "quiz":
        render_quiz_page()
    elif page == "results":
        render_results_page()
    else:
        render_landing_page()

# ============================================
# PAGE 1: LANDING PAGE
# ============================================

def render_landing_page():
    """Render the stunning landing/hero page."""
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-logo">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
        </div>
        <h1 class="hero-title gradient-text">AI-Powered Quiz Generator</h1>
        <p class="hero-subtitle">Transform PowerPoints into Intelligent Interactive Quizzes</p>
        <p style="color:var(--text-secondary);font-size:1.1rem;max-width:600px;margin:0 auto 2.5rem;">
            Upload any PPT and instantly generate AI-based MCQ quizzes with scoring and smart feedback.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started - Upload Your PPT", use_container_width=True):
            set_page("upload")
    
    # Feature Cards
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Smart PPT Analysis</div>
            <div class="feature-desc">Advanced parsing extracts text, concepts, and structure from your PowerPoint presentations with precision.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">AI Quiz Generation</div>
            <div class="feature-desc">Leverage AI to automatically generate intelligent multiple-choice questions tailored to your content.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <div class="feature-title">Instant Feedback</div>
            <div class="feature-desc">Get detailed scoring, performance analytics, and AI-powered explanations for every question.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
        <h2 style="font-size:2rem;font-weight:700;color:var(--text);">How It Works</h2>
        <div style="color:var(--text-secondary);margin-top:0.5rem;">Three simple steps to create your quiz</div>
    </div>
    """, unsafe_allow_html=True)
    
    steps_col1, steps_col2, steps_col3 = st.columns(3)
    
    with steps_col1:
        st.markdown("""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">📤</div>
            <div style="font-size:1.5rem;font-weight:700;color:var(--primary);margin-bottom:0.5rem;">01</div>
            <div style="font-weight:600;color:var(--text);margin-bottom:0.5rem;">Upload</div>
            <div style="color:var(--text-secondary);font-size:0.9rem;">Upload your PowerPoint file. We support both .ppt and .pptx formats.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with steps_col2:
        st.markdown("""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">⚙️</div>
            <div style="font-size:1.5rem;font-weight:700;color:var(--primary);margin-bottom:0.5rem;">02</div>
            <div style="font-weight:600;color:var(--text);margin-bottom:0.5rem;">Configure</div>
            <div style="color:var(--text-secondary);font-size:0.9rem;">Set question count, difficulty level, and timer preferences.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with steps_col3:
        st.markdown("""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">🎯</div>
            <div style="font-size:1.5rem;font-weight:700;color:var(--primary);margin-bottom:0.5rem;">03</div>
            <div style="font-weight:600;color:var(--text);margin-bottom:0.5rem;">Quiz & Learn</div>
            <div style="color:var(--text-secondary);font-size:0.9rem;">Take the quiz, get scored, and review AI-powered explanations.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        render_metric_card("Questions Generated", "1,000+", "📝")
    with stats_col2:
        render_metric_card("PPT Files Processed", "500+", "📊")
    with stats_col3:
        render_metric_card("Active Users", "250+", "👥")
    with stats_col4:
        render_metric_card("Avg. Score", "78%", "🎯")
    
    # Bottom CTA
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Start Creating Quizzes Now", use_container_width=True):
            set_page("upload")

# ============================================
# PAGE 2: FILE UPLOAD
# ============================================

def render_upload_page():
    """Render the file upload section with drag-and-drop."""
    
    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
        <h1 style="font-size:2.5rem;font-weight:700;color:var(--text);">
            📤 Upload Your Presentation
        </h1>
        <p style="color:var(--text-secondary);margin-top:0.5rem;">
            Drag and drop your PowerPoint file below to get started
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload area
    uploaded_file = st.file_uploader(
        "Choose a PowerPoint file",
        type=["ppt", "pptx"],
        help="Upload a .ppt or .pptx file to generate a quiz",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Validate file type
        file_ext = Path(uploaded_file.name).suffix.lower()
        if file_ext not in ('.ppt', '.pptx'):
            st.error("❌ Invalid file format. Please upload a .ppt or .pptx file.")
            return
        
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            with st.spinner("📖 Analyzing your presentation..."):
                # Extract content
                ppt_content = extract_ppt_content(tmp_path)
                
                # Store in session state
                st.session_state.ppt_content = ppt_content
                st.session_state.file_uploaded = True
                st.session_state.file_name = ppt_content["file_name"]
                st.session_state.file_size = ppt_content["file_size"]
                st.session_state.slide_count = ppt_content["slide_count"]
            
            # Success message
            st.success(f"✅ Successfully parsed {ppt_content['file_name']}!")
            
            # File info cards
            col1, col2, col3 = st.columns(3)
            with col1:
                render_metric_card("File Name", ppt_content["file_name"], "📄")
            with col2:
                render_metric_card("Slide Count", str(ppt_content["slide_count"]), "📑")
            with col3:
                render_metric_card("File Size", format_file_size(ppt_content["file_size"]), "💾")
            
            # Text preview
            st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-weight:600;color:var(--text);margin-bottom:1rem;">
                📝 Extracted Content Preview
            </div>
            """, unsafe_allow_html=True)
            
            for slide in ppt_content["slides"]:
                with st.expander(f"Slide {slide['slide_number']} ({slide['word_count']} words)"):
                    if slide["text"]:
                        st.markdown(f"""
                        <div style="background:var(--bg-glass);padding:1rem;border-radius:8px;
                                    border:1px solid var(--border-glass);color:var(--text-secondary);
                                    font-size:0.9rem;line-height:1.6;">
                            {slide['text']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No text content found on this slide.")
            
            # Continue button
            st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("⚙️ Configure Quiz Settings →", use_container_width=True):
                    set_page("configure")
        
        except PPTParserError as e:
            st.error(f"❌ {str(e)}")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    else:
        # Show upload prompt when no file is uploaded
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;">
            <div style="font-size:5rem;margin-bottom:1rem;animation:float 3s ease-in-out infinite;">📂</div>
            <div style="font-size:1.2rem;color:var(--text-secondary);margin-bottom:1rem;">
                Drag & drop your PowerPoint file here
            </div>
            <div style="color:var(--text-muted);font-size:0.9rem;">
                Supports .ppt and .pptx formats
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Back button
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    if st.button("← Back to Home", use_container_width=False):
        set_page("landing")

# ============================================
# PAGE 3: QUIZ CONFIGURATION
# ============================================

def render_configuration_page():
    """Render the quiz configuration panel."""
    
    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
        <h1 style="font-size:2.5rem;font-weight:700;color:var(--text);">
            ⚙️ Configure Your Quiz
        </h1>
        <p style="color:var(--text-secondary);margin-top:0.5rem;">
            Customize your quiz settings for the best learning experience
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show file info
    if st.session_state.file_uploaded:
        st.markdown(f"""
        <div class="glass-card" style="display:flex;align-items:center;gap:1rem;padding:1rem 1.5rem;margin-bottom:2rem;">
            <div style="font-size:2rem;">📄</div>
            <div>
                <div style="font-weight:600;color:var(--text);">{st.session_state.file_name}</div>
                <div style="color:var(--text-secondary);font-size:0.85rem;">
                    {st.session_state.slide_count} slides · {format_file_size(st.session_state.file_size)}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Configuration options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="font-weight:600;color:var(--text);margin-bottom:1rem;">
            📊 Question Settings
        </div>
        """, unsafe_allow_html=True)
        
        # Question count slider
        num_questions = st.slider(
            "Number of Questions",
            min_value=5,
            max_value=30,
            value=st.session_state.quiz_config.get("num_questions", 10),
            step=1,
            help="Choose how many questions to generate (5-30)"
        )
        
        # Difficulty selection with premium cards
        st.markdown("""
        <div style="font-weight:600;color:var(--text);margin:1rem 0;">
            🎯 Difficulty Level
        </div>
        """, unsafe_allow_html=True)
        
        difficulty = st.radio(
            "Select Difficulty",
            options=["Simple", "Medium", "Complex"],
            index=["Simple", "Medium", "Complex"].index(st.session_state.quiz_config.get("difficulty", "Medium")),
            horizontal=True,
            label_visibility="collapsed",
            help="Simple: Direct factual questions | Medium: Conceptual understanding | Complex: Analytical questions"
        )
        
        # Difficulty descriptions
        diff_descriptions = {
            "Simple": "📘 Basic recall questions based directly on slide content",
            "Medium": "📗 Conceptual questions testing understanding",
            "Complex": "📕 Analytical questions requiring critical thinking"
        }
        st.info(diff_descriptions[difficulty])
    
    with col2:
        st.markdown("""
        <div style="font-weight:600;color:var(--text);margin-bottom:1rem;">
            ⏱️ Timer Settings
        </div>
        """, unsafe_allow_html=True)
        
        timer_option = st.radio(
            "Timer Mode",
            options=["No Timer", "30 seconds per question", "60 seconds per question"],
            index=0,
            horizontal=False,
            help="Optionally add a time limit per question",
            label_visibility="visible"
        )
        
        timer_map = {
            "No Timer": "no_timer",
            "30 seconds per question": "30_sec",
            "60 seconds per question": "60_sec"
        }
        timer_setting = timer_map[timer_option]
        
        # AI Generation toggle
        st.markdown("""
        <div style="font-weight:600;color:var(--text);margin:1.5rem 0 1rem;">
            🤖 AI Generation
        </div>
        """, unsafe_allow_html=True)
        
        use_ai = st.checkbox(
            "Use AI for question generation",
            value=st.session_state.use_llm,
            help="Enable to use AI (OpenAI/DeepSeek) for smarter question generation. Requires API key in sidebar."
        )
        
        if use_ai and not st.session_state.api_key:
            st.warning("⚠️ Please enter an API key in the sidebar to use AI generation. Mock generation will be used as fallback.")
    
    # Store configuration
    st.session_state.quiz_config = {
        "num_questions": num_questions,
        "difficulty": difficulty,
        "timer": timer_setting
    }
    st.session_state.use_llm = use_ai and bool(st.session_state.api_key)
    
    # Generate button
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="generate-btn">', unsafe_allow_html=True)
        if st.button("🚀 Generate Quiz", use_container_width=True, type="primary"):
            set_page("processing")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Back button
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    if st.button("← Back to Upload", use_container_width=False):
        set_page("upload")

# ============================================
# PAGE 4: AI PROCESSING
# ============================================

def render_processing_page():
    """Render the AI processing animation screen."""
    
    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
        <h1 style="font-size:2.5rem;font-weight:700;color:var(--text);">
            🧠 AI Processing
        </h1>
        <p style="color:var(--text-secondary);margin-top:0.5rem;">
            Generating your intelligent quiz...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Processing animation placeholder
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Simulate processing steps
    steps = [
        "📄 Extracting slide content...",
        "🧠 Analyzing concepts...",
        "🤖 Generating MCQs...",
        "✅ Validating options..."
    ]
    
    for i, step_text in enumerate(steps):
        with progress_placeholder.container():
            render_processing_animation(i)
        
        with status_placeholder.container():
            st.markdown(f"""
            <div style="text-align:center;padding:0.5rem;color:var(--text-secondary);font-size:0.9rem;">
                {step_text}
            </div>
            """, unsafe_allow_html=True)
        
        # Simulate processing time
        time.sleep(0.8)
    
    # Actual quiz generation
    with status_placeholder.container():
        st.markdown("""
        <div style="text-align:center;padding:0.5rem;color:var(--text-secondary);font-size:0.9rem;">
            ✨ Finalizing your quiz...
        </div>
        """, unsafe_allow_html=True)
    
    try:
        # Generate the quiz
        ppt_content = st.session_state.ppt_content
        config = st.session_state.quiz_config
        
        if ppt_content is None:
            st.error("❌ No presentation content found. Please upload a file first.")
            set_page("upload")
            return
        
        # Initialize quiz generator
        generator = QuizGenerator(
            api_key=st.session_state.api_key if st.session_state.use_llm else None,
            api_url=st.session_state.api_url,
            model="gpt-3.5-turbo"
        )
        
        # Generate questions
        questions = generator.generate_quiz(
            slide_content=ppt_content,
            num_questions=config["num_questions"],
            difficulty=config["difficulty"],
            use_llm=st.session_state.use_llm
        )
        
        # Store questions in session state
        st.session_state.questions = questions
        st.session_state.current_question = 0
        st.session_state.user_answers = {}
        st.session_state.quiz_started = True
        st.session_state.quiz_completed = False
        
        # Set up timer if enabled
        timer_duration = get_timer_duration(config["timer"])
        if timer_duration:
            st.session_state.timer_duration = timer_duration
            st.session_state.timer_start = time.time()
            st.session_state.timer_running = True
        else:
            st.session_state.timer_duration = None
            st.session_state.timer_running = False
        
        # Initialize scorer
        from utils.scoring import QuizScorer
        st.session_state.scorer = QuizScorer()
        
        # Navigate to quiz
        set_page("quiz")
    
    except Exception as e:
        st.error(f"❌ Failed to generate quiz: {str(e)}")
        st.info("💡 Tip: Try reducing the number of questions or use a different difficulty level.")
        
        if st.button("← Back to Configuration"):
            set_page("configure")

# ============================================
# PAGE 5: QUIZ INTERFACE
# ============================================

def render_quiz_page():
    """Render the interactive quiz interface."""
    
    questions = st.session_state.questions
    if not questions:
        st.error("❌ No questions available. Please generate a quiz first.")
        set_page("landing")
        return
    
    total_questions = len(questions)
    current_idx = st.session_state.current_question
    current_q = questions[current_idx]
    
    # Quiz header
    st.markdown("""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <h1 style="font-size:2rem;font-weight:700;color:var(--text);">
            📝 Quiz Time
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress and timer row - fixed proportions to prevent overlap
    col1, col2, col3 = st.columns([3, 5, 4])
    
    with col1:
        st.markdown(f"""
        <div style="color:var(--text-secondary);font-size:0.9rem;">
            Question {current_idx + 1} of {total_questions}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        progress = (current_idx + 1) / total_questions
        st.progress(progress)
    
    with col3:
        # Timer display
        if st.session_state.timer_running and st.session_state.timer_duration:
            elapsed = time.time() - st.session_state.timer_start
            remaining = max(0, st.session_state.timer_duration - elapsed)
            
            if remaining <= 0:
                # Auto-advance on timer expiry
                st.session_state.user_answers[current_idx] = None
                if current_idx < total_questions - 1:
                    st.session_state.current_question += 1
                    st.session_state.timer_start = time.time()
                    st.rerun()
                else:
                    submit_quiz()
                    return
            
            timer_class = ""
            if remaining < 5:
                timer_class = "timer-critical"
            elif remaining < 10:
                timer_class = "timer-warning"
            
            st.markdown(f"""
            <div class="timer-container {timer_class}" style="justify-content:center;">
                <span>⏱️</span>
                <span class="timer-text">{format_time(int(remaining))}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Question card - premium futuristic
    st.markdown(f"""
    <div class="question-card">
        <div class="question-text">{current_q['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Options selection
    option_labels = ["A", "B", "C", "D"]
    selected = st.session_state.user_answers.get(current_idx)
    
    # Show selected answer indicator
    if selected:
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:0.8rem;padding:0.4rem 1rem;border-radius:10px;
                    background:rgba(0,229,255,0.06);border:1px solid rgba(0,229,255,0.15);">
            <span style="color:var(--text-secondary);font-size:0.85rem;">Selected: </span>
            <span style="color:#00E5FF;font-weight:700;">Option {selected}</span>
        </div>
        """, unsafe_allow_html=True)
    
    for i, (label, option) in enumerate(zip(option_labels, current_q['options'])):
        is_selected = selected == label
        
        # Use st.button with proper styling
        btn_label = f"{'✅ ' if is_selected else '○ '}{label}. {option}"
        if st.button(
            btn_label,
            key=f"q_{current_idx}_opt_{i}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.user_answers[current_idx] = label
            st.rerun()
    
    # Navigation buttons
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1, 1, 2, 1, 1])
    
    with nav_col1:
        if current_idx > 0:
            if st.button("← Previous", use_container_width=True):
                st.session_state.current_question -= 1
                st.rerun()
    
    with nav_col2:
        if current_idx < total_questions - 1:
            if st.button("Next →", use_container_width=True):
                st.session_state.current_question += 1
                if st.session_state.timer_running:
                    st.session_state.timer_start = time.time()
                st.rerun()
    
    with nav_col4:
        # Submit button
        if st.button("📊 Submit Quiz", use_container_width=True, type="primary"):
            submit_quiz()
    
    with nav_col5:
        # Question navigator
        answered_count = len(st.session_state.user_answers)
        st.markdown(f"""
        <div style="text-align:center;color:var(--text-secondary);font-size:0.85rem;padding:0.5rem;">
            {answered_count}/{total_questions} answered
        </div>
        """, unsafe_allow_html=True)
    
    # Question grid navigator
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:0.5rem;">
        Quick Navigation:
    </div>
    """, unsafe_allow_html=True)
    
    # Create a grid of question number buttons
    q_grid = st.columns(min(total_questions, 10))
    for i in range(total_questions):
        col_idx = i % 10
        with q_grid[col_idx]:
            answered = i in st.session_state.user_answers
            is_current = i == current_idx
            
            btn_type = "primary" if is_current else ("secondary" if answered else "tertiary")
            label = f"✓" if answered else str(i + 1)
            
            if st.button(label, key=f"nav_q_{i}", use_container_width=True, type=btn_type):
                st.session_state.current_question = i
                st.rerun()


def submit_quiz():
    """Submit the quiz and calculate results."""
    questions = st.session_state.questions
    scorer = st.session_state.scorer
    
    if scorer is None:
        from utils.scoring import QuizScorer
        scorer = QuizScorer()
        st.session_state.scorer = scorer
    
    # Record all answers
    for idx in range(len(questions)):
        answer = st.session_state.user_answers.get(idx)
        if answer:
            scorer.record_answer(idx, answer)
    
    # Calculate results
    results = scorer.calculate_results(questions)
    st.session_state.results = results
    st.session_state.quiz_completed = True
    st.session_state.timer_running = False
    
    # Show confetti for high scores
    if results["percentage"] >= 75:
        st.session_state.show_confetti = True
    
    set_page("results")


# ============================================
# PAGE 6: RESULTS DASHBOARD
# ============================================

def render_results_page():
    """Render the stunning results dashboard."""
    
    results = st.session_state.results
    if not results:
        st.error("❌ No results available. Please complete a quiz first.")
        set_page("landing")
        return
    
    # Show confetti for high scores
    if st.session_state.show_confetti:
        inject_confetti()
    
    # Header
    perf = results["performance_message"]
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:2rem;">
        <h1 style="font-size:2.5rem;font-weight:700;color:var(--text);">
            {perf['emoji']} Quiz Complete!
        </h1>
        <h2 style="font-size:1.5rem;font-weight:600;color:var(--text);margin-top:0.5rem;">
            {perf['title']}
        </h2>
        <p style="color:var(--text-secondary);margin-top:0.5rem;max-width:500px;margin-left:auto;margin-right:auto;">
            {perf['message']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Score Circle
    percentage = results["percentage"]
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Determine score class
        if percentage >= 90:
            score_class = "score-outstanding"
        elif percentage >= 75:
            score_class = "score-excellent"
        elif percentage >= 50:
            score_class = "score-good"
        else:
            score_class = "score-needs-improvement"
        
        st.markdown(f"""
        <div style="display:flex;justify-content:center;margin:2rem 0;">
            <div class="score-circle {score_class}" style="--percentage:{percentage}%;">
                <div class="score-circle-inner">
                    <div class="score-number">{results['score']}/{results['total_questions']}</div>
                    <div class="score-label">Score</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Accuracy", f"{percentage}%", "🎯", 
                          "success" if percentage >= 75 else "warning")
    with col2:
        render_metric_card("Correct", str(results["correct_count"]), "✅", "success")
    with col3:
        render_metric_card("Wrong", str(results["wrong_count"]), "❌", "danger")
    with col4:
        render_metric_card("Unanswered", str(results["unanswered"]), "⏭️", "primary")
    
    # Charts
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("""
        <div style="font-weight:600;color:var(--text);margin-bottom:1rem;">
            📊 Score Distribution
        </div>
        """, unsafe_allow_html=True)
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=["Correct", "Wrong", "Unanswered"],
            values=[results["correct_count"], results["wrong_count"], results["unanswered"]],
            marker=dict(colors=["#10B981", "#EF4444", "#64748B"]),
            textinfo="label+percent",
            hole=0.6,
            textfont=dict(color="white")
        )])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94A3B8"),
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        st.markdown("""
        <div style="font-weight:600;color:var(--text);margin-bottom:1rem;">
            📈 Performance Overview
        </div>
        """, unsafe_allow_html=True)
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=["Correct", "Wrong", "Unanswered"],
                y=[results["correct_count"], results["wrong_count"], results["unanswered"]],
                marker=dict(
                    color=["#10B981", "#EF4444", "#64748B"],
                    line=dict(color=["#34D399", "#F87171", "#94A3B8"], width=2)
                ),
                text=[results["correct_count"], results["wrong_count"], results["unanswered"]],
                textposition="outside",
                textfont=dict(color="white", size=16)
            )
        ])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94A3B8"),
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Count"),
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            bargap=0.5
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Review
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-weight:600;color:var(--text);margin-bottom:1rem;font-size:1.2rem;">
        📋 Detailed Question Review
    </div>
    """, unsafe_allow_html=True)
    
    for idx, r in enumerate(results["results"]):
        is_correct = r["is_correct"]
        was_answered = r["was_answered"]
        
        # Determine card style
        if not was_answered:
            border_color = "rgba(100, 116, 139, 0.3)"
            icon = "⏭️"
            status_text = "Skipped"
        elif is_correct:
            border_color = "rgba(16, 185, 129, 0.3)"
            icon = "✅"
            status_text = "Correct"
        else:
            border_color = "rgba(239, 68, 68, 0.3)"
            icon = "❌"
            status_text = "Incorrect"
        
        st.markdown(f"""
        <div class="glass-card" style="margin:1rem 0;border-color:{border_color};">
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:1rem;">
                <div style="font-weight:600;color:var(--text);">
                    Question {idx + 1}: {r['question']}
                </div>
                <div style="display:flex;align-items:center;gap:0.5rem;">
                    <span class="badge {'badge-success' if is_correct else ('badge-danger' if was_answered else '')}">
                        {icon} {status_text}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Show options with correct/wrong highlighting
        option_labels = ["A", "B", "C", "D"]
        for opt_idx, (label, option) in enumerate(zip(option_labels, r["options"])):
            is_user_ans = r["user_answer"] == label
            is_correct_ans = r["correct_answer"] == label
            
            if is_correct_ans:
                st.success(f"✅ {label}. {option} (Correct Answer)")
            elif is_user_ans and not is_correct_ans:
                st.error(f"❌ {label}. {option} (Your Answer)")
            else:
                st.markdown(f"""
                <div style="padding:0.5rem 1rem;color:var(--text-secondary);">
                    {label}. {option}
                </div>
                """, unsafe_allow_html=True)
        
        # Explanation
        st.markdown(f"""
        <div style="margin-top:1rem;padding:1rem;background:rgba(139,92,246,0.08);
                    border-radius:8px;border:1px solid rgba(139,92,246,0.15);">
            <div style="font-weight:600;color:var(--primary-light);margin-bottom:0.25rem;">💡 Explanation</div>
            <div style="color:var(--text-secondary);font-size:0.9rem;">{r['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Try Again", use_container_width=True):
            # Reset quiz state
            st.session_state.current_question = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_started = False
            st.session_state.quiz_completed = False
            st.session_state.results = None
            st.session_state.show_confetti = False
            set_page("configure")
    
    with col2:
        if st.button("📤 New File", use_container_width=True):
            # Full reset
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("🏠 Home", use_container_width=True):
            set_page("landing")


# ============================================
# APP ENTRY POINT
# ============================================

if __name__ == "__main__":
    main()