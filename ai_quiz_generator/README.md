# 🧠 AI Quiz Generator

> **Transform PowerPoint Presentations into Intelligent Interactive Quizzes**

![Version](https://img.shields.io/badge/version-1.0.0-blueviolet)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Overview

AI Quiz Generator is a premium, production-quality Streamlit application that automatically converts PowerPoint presentations into interactive multiple-choice quizzes. Powered by AI (OpenAI/DeepSeek compatible) with an intelligent fallback mock generator, it provides a stunning, futuristic user experience with real-time scoring, analytics, and detailed feedback.

### 🎯 Key Features

- **📊 Smart PPT Analysis** - Advanced parsing extracts text, concepts, and structure from PowerPoint files
- **🤖 AI-Powered Generation** - Leverages LLMs for intelligent question creation (with smart fallback)
- **🎨 Premium UI/UX** - Glassmorphism design, animated gradients, floating particles, neon glow effects
- **⏱️ Timed Quizzes** - Optional per-question timer (30s/60s) for challenge mode
- **📈 Rich Analytics** - Interactive charts, circular score indicators, performance breakdowns
- **💡 AI Explanations** - Detailed explanations for every question to enhance learning
- **🎉 Celebratory Effects** - Confetti animations for high scores
- **⚙️ Fully Configurable** - Adjustable question count (5-30), difficulty levels, and timer settings

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. **Clone or navigate to the project directory:**

```bash
cd ai_quiz_generator
```

2. **Create a virtual environment (recommended):**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the application:**

```bash
streamlit run app.py
```

5. **Open your browser:**
   - The app will open automatically at `http://localhost:8501`
   - If not, navigate to the URL shown in your terminal

---

## 📖 Usage Guide

### 1. Landing Page
- Stunning hero section with animated gradient text
- Feature overview cards
- Click "Get Started" to begin

### 2. Upload Presentation
- Drag & drop or browse for `.ppt` or `.pptx` files
- View extracted slide content in expandable cards
- See file stats (slide count, size, word count)

### 3. Configure Quiz
- **Question Count**: 5-30 questions (slider)
- **Difficulty**: Simple / Medium / Complex
- **Timer**: No timer / 30s per question / 60s per question
- **AI Generation**: Toggle AI-powered generation (requires API key)

### 4. AI Processing
- Animated processing screen with progress indicators
- AI brain visualization
- Step-by-step generation status

### 5. Take the Quiz
- One question at a time with progress tracking
- Animated option selection
- Timer display (if enabled)
- Quick navigation between questions
- Submit anytime

### 6. View Results
- Circular score indicator
- Performance metrics (accuracy, correct/wrong/unanswered)
- Interactive charts (pie chart + bar chart)
- Detailed question-by-question review
- AI explanations for each answer
- Confetti celebration for high scores

---

## 🔧 Configuration

### API Setup (Optional - for AI Generation)

The app works without an API key using intelligent mock generation. For AI-powered questions:

1. **OpenAI API Key:**
   - Get your key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Enter it in the sidebar under "API Configuration"

2. **DeepSeek API (Alternative):**
   - Get your key from [DeepSeek](https://platform.deepseek.com/)
   - Enter the API key and set API URL to: `https://api.deepseek.com/v1`

3. **Custom API Endpoint:**
   - Supports any OpenAI-compatible API
   - Set the API URL to your custom endpoint

### Sidebar Controls

- **API Configuration**: API key, URL, and model settings
- **Navigation**: Quick access to Home, Resume Quiz, View Results
- **Reset**: Clear all data and start fresh

---

## 🏗️ Project Architecture

```
ai_quiz_generator/
│
├── app.py                    # Main application (Streamlit)
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation
│
├── assets/
│   └── styles.css            # Premium custom CSS (glassmorphism, animations)
│
├── utils/
│   ├── ppt_parser.py         # PowerPoint text extraction
│   ├── quiz_generator.py     # AI + mock quiz generation
│   ├── scoring.py            # Scoring and result calculation
│   └── helpers.py            # UI helpers, session state, utilities
│
└── sample_output/
    └── quiz.json             # Sample quiz output format
```

### Module Breakdown

| Module | Responsibility |
|--------|---------------|
| `app.py` | Streamlit UI, page routing, session management |
| `ppt_parser.py` | Extract text from .ppt/.pptx files |
| `quiz_generator.py` | Generate MCQs via LLM or intelligent fallback |
| `scoring.py` | Calculate scores, performance analysis |
| `helpers.py` | CSS injection, animations, utility functions |
| `styles.css` | All custom styling (700+ lines of premium CSS) |

---

## 🎨 Design System

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Background | `#070B14` | Deep space dark |
| Card | `rgba(255,255,255,0.08)` | Glassmorphism |
| Primary | `#8B5CF6` | Purple accent |
| Secondary | `#3B82F6` | Blue accent |
| Accent | `#06B6D4` | Cyan highlight |
| Text | `#FFFFFF` | Primary text |
| Muted | `#94A3B8` | Secondary text |

### Design Features

- **Glassmorphism**: Frosted glass card effects with backdrop blur
- **Animated Gradients**: Moving gradient text and backgrounds
- **Neon Glow**: Subtle glow effects on interactive elements
- **Floating Particles**: Dynamic background particle system
- **Smooth Transitions**: CSS transitions on all interactive elements
- **Responsive**: Adapts to mobile and desktop viewports

---

## 🧪 Sample Output

Generated quiz questions follow this JSON format:

```json
[
  {
    "question": "What is the primary function of a PowerPoint presentation?",
    "options": [
      "To create complex databases",
      "To visually communicate information and ideas",
      "To edit video files",
      "To write computer programs"
    ],
    "correct_answer": "B",
    "explanation": "PowerPoint is designed for creating visual presentations..."
  }
]
```

See `sample_output/quiz.json` for a complete example.

---

## 🛠️ Development

### Adding New Features

1. **New Page**: Add a new page function in `app.py` and add routing in `main()`
2. **New Utility**: Create a new file in `utils/` and import in `app.py`
3. **New CSS**: Add styles to `assets/styles.css` using the existing design system

### Code Style

- Type hints for all functions
- Comprehensive docstrings
- Modular architecture with single responsibility
- Error handling throughout
- Session state management for persistence

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - The amazing web framework
- [python-pptx](https://python-pptx.readthedocs.io/) - PowerPoint file processing
- [Plotly](https://plotly.com/) - Interactive visualizations
- [OpenAI](https://openai.com/) - AI language models

---

<div align="center">
  <sub>Built with ❤️ for the AI Quiz Generator Project</sub>
</div>