"""
Helpers Module
==============
Utility functions for the AI Quiz Generator application.
Provides session state management, UI helpers, and configuration utilities.
"""

import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


def init_session_state():
    """
    Initialize all required Streamlit session state variables.
    Call this at the start of the app to ensure all states exist.
    """
    defaults = {
        "page": "landing",
        "ppt_content": None,
        "questions": None,
        "current_question": 0,
        "user_answers": {},
        "quiz_started": False,
        "quiz_completed": False,
        "results": None,
        "scorer": None,
        "timer_start": None,
        "timer_duration": None,
        "timer_running": False,
        "api_key": None,
        "api_url": None,
        "use_llm": False,
        "quiz_config": {
            "num_questions": 10,
            "difficulty": "Medium",
            "timer": "no_timer"
        },
        "processing": False,
        "processing_step": 0,
        "show_confetti": False,
        "file_uploaded": False,
        "file_name": "",
        "file_size": 0,
        "slide_count": 0,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_page(page: str):
    """
    Set the current page in session state.
    
    Args:
        page: Page name to navigate to
    """
    st.session_state.page = page
    st.rerun()


def load_css():
    """Load and inject custom CSS into the Streamlit app."""
    css_path = Path(__file__).parent.parent / "assets" / "styles.css"
    
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found. Using default styles.")


def inject_particles():
    """
    Inject floating particle background animation into the app.
    Creates a canvas of animated particles with cosmic color palette.
    """
    particles_html = """
    <div class="particles-container" id="particles-container"></div>
    <script>
        const container = document.getElementById('particles-container');
        const colors = ['#00E5FF', '#FF2E9A', '#14F1D9', '#4F46E5', '#FFD166'];
        
        for (let i = 0; i < 60; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            const size = Math.random() * 4 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.background = colors[Math.floor(Math.random() * colors.length)];
            particle.style.animationDuration = (Math.random() * 25 + 15) + 's';
            particle.style.animationDelay = (Math.random() * 25) + 's';
            particle.style.boxShadow = '0 0 ' + (size * 2) + 'px ' + colors[Math.floor(Math.random() * colors.length)];
            particle.style.opacity = Math.random() * 0.4 + 0.1;
            container.appendChild(particle);
        }
    </script>
    """
    st.markdown(particles_html, unsafe_allow_html=True)


def inject_confetti():
    """
    Inject confetti celebration animation with premium colors.
    Creates falling confetti pieces for high scores.
    """
    confetti_html = """
    <div id="confetti-container"></div>
    <script>
        const confettiContainer = document.getElementById('confetti-container');
        const confettiColors = ['#00E5FF', '#FF2E9A', '#14F1D9', '#4F46E5', '#FFD166', '#10B981', '#EF4444', '#FFFFFF'];
        const shapes = ['50%', '2px', '0'];
        
        for (let i = 0; i < 120; i++) {
            const piece = document.createElement('div');
            piece.className = 'confetti-piece';
            piece.style.left = Math.random() * 100 + '%';
            piece.style.background = confettiColors[Math.floor(Math.random() * confettiColors.length)];
            const size = Math.random() * 8 + 5;
            piece.style.width = size + 'px';
            piece.style.height = (Math.random() * 8 + 5) + 'px';
            piece.style.borderRadius = shapes[Math.floor(Math.random() * shapes.length)];
            piece.style.animationDuration = (Math.random() * 2.5 + 2) + 's';
            piece.style.animationDelay = (Math.random() * 4) + 's';
            piece.style.transform = 'rotate(' + (Math.random() * 360) + 'deg)';
            piece.style.boxShadow = '0 0 6px ' + piece.style.background;
            confettiContainer.appendChild(piece);
        }
        
        setTimeout(() => {
            if (confettiContainer) confettiContainer.innerHTML = '';
        }, 6000);
    </script>
    """
    st.markdown(confetti_html, unsafe_allow_html=True)


def render_svg_logo(size: int = 80) -> str:
    """
    Generate an SVG logo for the app with holographic effects.
    
    Args:
        size: Size of the logo in pixels
        
    Returns:
        HTML string with SVG logo
    """
    return f"""
    <div style="width:{size}px;height:{size}px;margin:0 auto 2rem;position:relative;
                display:flex;align-items:center;justify-content:center;">
        <div style="position:absolute;width:{size * 1.4}px;height:{size * 1.4}px;
                    border:1px solid rgba(0,229,255,0.15);border-radius:50%;
                    animation:ringRotate 6s linear infinite;"></div>
        <div style="position:absolute;width:{size * 1.7}px;height:{size * 1.7}px;
                    border:1px solid rgba(255,46,154,0.1);border-radius:50%;
                    animation:ringRotate 6s linear infinite reverse;"></div>
        <div style="width:{size}px;height:{size}px;background:radial-gradient(circle at 30% 30%,
                    rgba(0,229,255,0.3),rgba(79,70,229,0.2),rgba(255,46,154,0.1));
                    border-radius:50%;display:flex;align-items:center;justify-content:center;
                    box-shadow:0 0 60px rgba(0,229,255,0.2),0 0 120px rgba(0,229,255,0.1),
                    inset 0 0 60px rgba(255,46,154,0.1);
                    animation:orbPulse 4s ease-in-out infinite;">
            <svg width="{size * 0.5}" height="{size * 0.5}" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
        </div>
    </div>
    """


def render_metric_card(label: str, value: str, icon: str, color: str = "primary"):
    """
    Render a premium metric card using HTML.
    
    Args:
        label: Metric label
        value: Metric value
        icon: Emoji icon
        color: Color theme (primary, success, danger, warning)
    """
    border_colors = {
        "primary": "rgba(0, 229, 255, 0.2)",
        "success": "rgba(16, 185, 129, 0.2)",
        "danger": "rgba(239, 68, 68, 0.2)",
        "warning": "rgba(255, 209, 102, 0.2)"
    }
    glow = {
        "primary": "rgba(0, 229, 255, 0.08)",
        "success": "rgba(16, 185, 129, 0.08)",
        "danger": "rgba(239, 68, 68, 0.08)",
        "warning": "rgba(255, 209, 102, 0.08)"
    }
    
    border = border_colors.get(color, "rgba(255,255,255,0.1)")
    g = glow.get(color, "rgba(255,255,255,0.05)")
    
    html = f"""
    <div class="glass-card" style="text-align:center;padding:1.8rem 1.2rem;border-color:{border};">
        <div style="font-size:2.2rem;margin-bottom:0.8rem;filter:drop-shadow(0 0 15px {g});">{icon}</div>
        <div style="font-size:2.2rem;font-weight:800;color:var(--text);font-family:var(--font-heading);">{value}</div>
        <div style="color:var(--text-secondary);font-size:0.85rem;margin-top:0.4rem;
                    text-transform:uppercase;letter-spacing:0.06em;font-weight:500;">{label}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_processing_animation(step: int = 0):
    """
    Render the AI processing animation with holographic supercomputer visuals.
    
    Args:
        step: Current processing step (0-3)
    """
    steps = [
        {"icon": "📄", "label": "Extracting slide content...", "desc": "Scanning presentation data"},
        {"icon": "🧠", "label": "Analyzing concepts...", "desc": "Identifying key topics & patterns"},
        {"icon": "🤖", "label": "Generating MCQs...", "desc": "Creating intelligent questions"},
        {"icon": "✅", "label": "Validating options...", "desc": "Quality assurance check"},
    ]
    
    # Holographic supercomputer animation
    holo_html = """
    <div style="position:relative;text-align:center;padding:2.5rem 0 1.5rem;">
        <div style="position:relative;display:inline-block;">
            <div class="holo-ring" style="width:160px;height:160px;"></div>
            <div class="holo-ring" style="width:130px;height:130px;animation-direction:reverse;border-color:rgba(255,46,154,0.12);"></div>
            <div class="holo-ring" style="width:100px;height:100px;border-color:rgba(79,70,229,0.15);"></div>
            <div style="position:relative;z-index:2;font-size:3.5rem;">🧠</div>
        </div>
        <div style="height:2px;background:linear-gradient(90deg,transparent,#00E5FF,transparent);
                    margin:0.5rem auto;width:200px;opacity:0.5;
                    animation:scanMove 2s ease-in-out infinite;"></div>
    </div>
    """
    st.markdown(holo_html, unsafe_allow_html=True)
    
    # Progress bar
    progress = (step + 1) / len(steps)
    st.progress(progress)
    
    # Step indicators with premium styling
    for i, s in enumerate(steps):
        if i < step:
            icon_display = "<span style='color:#10B981;'>✓</span>"
            border = "rgba(16, 185, 129, 0.3)"
            bg = "rgba(16, 185, 129, 0.05)"
            icon_bg = "rgba(16, 185, 129, 0.15)"
            box_shadow = ""
        elif i == step:
            icon_display = "<span style='color:#00E5FF;'>⏳</span>"
            border = "rgba(0, 229, 255, 0.3)"
            bg = "rgba(0, 229, 255, 0.05)"
            icon_bg = "rgba(0, 229, 255, 0.15)"
            box_shadow = "box-shadow:0 0 30px rgba(0,229,255,0.08);"
        else:
            icon_display = "<span style='color:rgba(255,255,255,0.3);'>⭕</span>"
            border = "rgba(255, 255, 255, 0.06)"
            bg = "rgba(255, 255, 255, 0.02)"
            icon_bg = "rgba(255, 255, 255, 0.04)"
            box_shadow = ""
        
        step_html = f"""
        <div style="display:flex;align-items:center;gap:1rem;padding:1rem 1.2rem;margin:0.6rem 0;
                    border-radius:14px;background:{bg};border:1px solid {border};
                    transition:all 0.5s cubic-bezier(0.16,1,0.3,1);{box_shadow}">
            <div style="width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;
                        font-size:1.2rem;flex-shrink:0;background:{icon_bg};
                        {'box-shadow:0 0 20px rgba(0,229,255,0.15);animation:iconPulse 1.5s ease-in-out infinite;' if i == step else ''}">
                {s['icon']}
            </div>
            <div style="flex:1;">
                <div style="font-weight:600;color:var(--text);font-size:0.95rem;">{s['label']}</div>
                <div style="font-size:0.8rem;color:var(--text-secondary);">{s['desc']}</div>
            </div>
            <div style="font-size:1.1rem;">{icon_display}</div>
        </div>
        """
        st.markdown(step_html, unsafe_allow_html=True)


def render_option_card(option_text: str, option_label: str, is_selected: bool = False, 
                       is_correct: bool = False, is_wrong: bool = False, disabled: bool = False):
    """
    Render a quiz option card.
    
    Args:
        option_text: The option text
        option_label: A, B, C, or D
        is_selected: Whether this option is currently selected
        is_correct: Whether this is the correct answer
        is_wrong: Whether this is a wrong answer
        disabled: Whether the option is disabled
        
    Returns:
        HTML string for the option card
    """
    classes = ["option-btn"]
    if is_selected: classes.append("selected")
    if is_correct: classes.append("correct")
    if is_wrong: classes.append("wrong")
    
    class_str = " ".join(classes)
    
    return f"""
    <div class="{class_str}" {'style="pointer-events:none;opacity:0.7;"' if disabled else ''}>
        <span class="option-label">{option_label}</span>
        <span style="flex:1;color:inherit;font-weight:inherit;">{option_text}</span>
        {'<span style="color:#10B981;font-weight:700;">✓</span>' if is_correct and is_selected else ''}
        {'<span style="color:#EF4444;font-weight:700;">✗</span>' if is_wrong else ''}
    </div>
    """


def format_time(seconds: int) -> str:
    """
    Format seconds into MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def get_timer_duration(timer_setting: str) -> Optional[int]:
    """
    Get timer duration in seconds from timer setting.
    
    Args:
        timer_setting: "no_timer", "30_sec", or "60_sec"
        
    Returns:
        Duration in seconds, or None for no timer
    """
    durations = {
        "no_timer": None,
        "30_sec": 30,
        "60_sec": 60
    }
    return durations.get(timer_setting)


def validate_api_key(api_key: str) -> bool:
    """
    Validate that an API key looks reasonable.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if the key looks valid
    """
    if not api_key or len(api_key) < 10:
        return False
    return True


def get_app_info() -> Dict:
    """
    Get application information for display.
    
    Returns:
        Dictionary with app info
    """
    return {
        "name": "AI Quiz Generator",
        "version": "1.0.0",
        "description": "Transform PowerPoint presentations into intelligent interactive quizzes",
        "author": "AI Quiz Generator Team",
        "year": datetime.now().year
    }


def create_sample_quiz() -> List[Dict]:
    """
    Create a sample quiz for demonstration/testing purposes.
    
    Returns:
        List of sample question dictionaries
    """
    return [
        {
            "question": "What is the primary function of a PowerPoint presentation?",
            "options": [
                "To create complex databases",
                "To visually communicate information and ideas",
                "To edit video files",
                "To write computer programs"
            ],
            "correct_answer": "B",
            "explanation": "PowerPoint is designed for creating visual presentations to communicate information effectively."
        },
        {
            "question": "Which of the following is NOT a standard PowerPoint view?",
            "options": [
                "Normal view",
                "Slide Sorter view",
                "Database view",
                "Slide Show view"
            ],
            "correct_answer": "C",
            "explanation": "Database view is not a standard PowerPoint view. The standard views include Normal, Slide Sorter, Reading, and Slide Show."
        },
        {
            "question": "What does AI stand for in the context of modern technology?",
            "options": [
                "Automated Integration",
                "Artificial Intelligence",
                "Advanced Interface",
                "Algorithmic Input"
            ],
            "correct_answer": "B",
            "explanation": "AI stands for Artificial Intelligence, which refers to the simulation of human intelligence by machines."
        },
        {
            "question": "What is the purpose of slide transitions in PowerPoint?",
            "options": [
                "To change the font style",
                "To add animation effects between slides",
                "To insert images",
                "To save the presentation"
            ],
            "correct_answer": "B",
            "explanation": "Slide transitions are visual effects that occur when moving from one slide to the next during a presentation."
        },
        {
            "question": "Which file extension is used for PowerPoint presentations?",
            "options": [
                ".docx",
                ".xlsx",
                ".pptx",
                ".pdf"
            ],
            "correct_answer": "C",
            "explanation": "The .pptx extension is the standard file format for PowerPoint presentations."
        }
    ]