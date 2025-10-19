# Prototype3 - Hardcoded Questions with AI Summaries# CyberHubs AI Assessment Platform - Prototype2

## OverviewA **fully AI-driven** cybersecurity skills assessment platform built with Flask, Python, and Google Gemini AI. Features modular architecture, comprehensive debugging, and personalized learning paths.

Prototype3 is a simplified version of the CyberHubs Assessment Platform that uses **hardcoded questions from a JSON file** and only uses AI for generating personalized **summaries and recommendations** at the end of assessments.

## 🚀 Features

## Architecture

- **AI-Powered Questions**: Every question generated dynamically by Google Gemini AI

### Key Differences from Prototype2- **Personalized Feedback**: AI-generated explanations and learning recommendations

- ✅ **No AI question generation** - all questions loaded from `questions.json`- **Multiple Domains**:

- ✅ **No MySQL database** - questions are hardcoded in JSON - Network Security (Firewalls, IDS/IPS, VPNs)

- ✅ **No multi-layer caching** - simple JSON loading at startup - Secure Coding (OWASP, SQL Injection, XSS)

- ✅ **AI only for results** - Gemini API used only for summaries and recommendations - Incident Response (Forensics, Containment, Threat Hunting)

- ✅ **Simpler, faster, more reliable** - no rate limits during assessments- **Difficulty Levels**: Beginner, Intermediate, Advanced

- **Progress Tracking**: Dashboard with statistics, history, and badges

### Components- **Modular Architecture**: Separate services and routes for easy debugging

- **Comprehensive Logging**: DEBUG-level logging throughout the application

#### Services

- **`question_bank.py`** - Loads questions from JSON, tracks used questions, random selection## 📁 Project Structure

- **`gemini_service.py`** - AI summary and recommendation generation (NOT for questions)

- **`assessment_service.py`** - Assessment flow, scoring, adaptive difficulty```

Prototype2/

#### Question Bank├── app.py # Main Flask application

- **Location**: `questions.json` (root directory)├── requirements.txt # Python dependencies

- **Format**: Structured JSON with domains, difficulties, and question data├── .env.example # Environment configuration template

- **Loading**: Loaded once at application startup├── services/ # Business logic services

- **Selection**: Random unused questions per domain/difficulty│ ├── **init**.py

│ ├── gemini_service.py # AI question/feedback generation

## Features│ └── assessment_service.py # Assessment logic & scoring

├── routes/ # Route blueprints

### Hardcoded Question Management│ ├── **init**.py

````python│ ├── home.py                    # Home page route

# Load questions at startup│   ├── assessment.py              # Assessment flow routes

question_bank = QuestionBank()│   ├── dashboard.py               # Dashboard & stats routes

│   └── api.py                     # JSON API endpoints

# Get a random unused question└── templates/                      # Jinja2 templates

question = question_bank.get_question(    ├── base.html                  # Base template with navigation

    domain='network-security',    ├── home.html                  # Landing page

    difficulty='intermediate'    ├── assessment/

)    │   ├── start.html             # Domain/difficulty selection

    │   ├── question.html          # Question display

# Get question counts    │   ├── feedback.html          # Answer feedback

counts = question_bank.get_question_count()    │   └── results.html           # Final results

# {'total': 900, 'by_domain': {...}, 'by_difficulty': {...}}    ├── dashboard/

    │   └── index.html             # Dashboard overview

# Reset used questions (start fresh)    └── errors/

question_bank.reset_used_questions()        ├── 404.html               # Not found page

```        └── 500.html               # Server error page

````

### AI-Powered Results

````python## 🛠️ Setup Instructions

# Generate personalized summary

gemini_service = get_gemini_service()### Prerequisites

summary = gemini_service.generate_assessment_summary(results_data)

- Python 3.8 or higher

# Generate learning recommendations- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

recommendations = gemini_service.generate_recommendations(results_data)

```### Installation



### Adaptive Difficulty1. **Clone the repository** (if not already done)

- Questions adapt based on performance during assessment

- No need to regenerate questions - just selects from different difficulty levels   ```bash

- Seamless progression: beginner → intermediate → advanced   cd Prototype2

````

## Setup

2. **Create virtual environment**

### 1. Install Dependencies

`bash   `bash

pip install -r requirements.txt python -m venv venv

```source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### 2. Configure Environment

Create `.env` file:3. **Install dependencies**

````env

GEMINI_API_KEY=your_gemini_api_key_here   ```bash

SECRET_KEY=your_secret_key_here   pip install -r requirements.txt

FLASK_DEBUG=True   ```

````

4. **Configure environment variables**

### 3. Verify Question Bank

`bash   `bash

# Check questions.json exists and is valid cp .env.example .env

python -c "import json; data = json.load(open('questions.json')); print(f'Loaded {len(data.get(\"questions\", {}))} question categories')" ```

````

   Edit `.env` and add your Google Gemini API key:

### 4. Run Application

```bash   ```

python app.py   GOOGLE_API_KEY=your_api_key_here

```   SECRET_KEY=your_secret_key_here

   DEBUG=True

Application will start on http://localhost:5000   ```



## Question Format5. **Run the application**



Questions in `questions.json` follow this structure:   ```bash

   python app.py

```json   ```

{

  "questions": {6. **Open your browser**

    "network-security_beginner": [   Navigate to: `http://localhost:5000`

      {

        "title": "What is a firewall?",## 🎯 Usage Guide

        "question": "Which statement best describes a firewall?",

        "domain": "network-security",### Starting an Assessment

        "difficulty": "beginner",

        "options": [1. **Select Domain**: Choose from Network Security, Secure Coding, or Incident Response

          "A device that monitors and controls network traffic",2. **Choose Difficulty**: Beginner, Intermediate, or Advanced

          "A software that encrypts files",3. **Set Question Count**: 5, 10, or 15 questions

          "A hardware component for storage",4. **Start Assessment**: Answer AI-generated questions

          "An antivirus program"

        ],### During Assessment

        "correct": 0,

        "explanation": "A firewall is a network security device that monitors and controls incoming and outgoing network traffic based on predetermined security rules.",- **Answer Questions**: Select from 4 multiple-choice options

        "learningPoints": [- **Get Feedback**: Receive instant AI-powered explanations

          "Firewalls act as barriers between trusted and untrusted networks",- **Track Progress**: See your score and time for each question

          "They can be hardware or software-based"- **Navigate**: Move forward through questions (no backward navigation)

        ],

        "sources": [### After Assessment

          "https://example.com/firewall-guide"

        ]- **View Results**: See overall score, performance metrics, and AI learning path

      }- **Dashboard**: Track progress across all domains and difficulty levels

    ],- **History**: Review past assessments and identify trends

    "network-security_intermediate": [...],- **Badges**: Earn achievements for milestones

    "network-security_advanced": [...],

    "secure-coding_beginner": [...],## 🏗️ Architecture

    ...

  },### Modular Design

  "metadata": {

    "version": "1.0",Every service and route is a **separate module** for easy debugging and maintenance:

    "last_updated": "2024-01-01",

    "total_questions": 900- **Services Layer**: Business logic (AI generation, scoring, statistics)

  }- **Routes Layer**: HTTP request handling (blueprints for each feature)

}- **Templates Layer**: Jinja2 templates with responsive design

````

### Logging & Debugging

## API Usage

- **Comprehensive Logging**: DEBUG-level logs in every function

### Assessment Flow- **Try/Except Blocks**: Error handling throughout

1. **Start Assessment** - `POST /assessment/start`- **Debug Panel**: Template-based debug info (route, method, session)

   - Select domain and number of questions- **Console Logging**: Frontend debugging with console.log

   - Creates assessment session

### Session Management

2. **Answer Questions** - `GET/POST /assessment/question`

   - Displays question from hardcoded bank- **Server-side Sessions**: Flask-Session with filesystem storage

   - Submits answer- **Assessment State**: Track current question, answers, and progress

   - Adapts difficulty based on performance- **User Stats**: Persistent statistics across sessions

3. **View Results** - `GET /assessment/results`## 🧪 API Endpoints

   - Calculates score

   - Generates AI summary (uses Gemini API)### JSON API Routes

   - Generates AI recommendations (uses Gemini API)

- `GET /api/health` - Health check

### Gemini API Calls- `POST /api/generate-question` - Generate single AI question

- **Only 2 API calls per assessment**:- `GET /api/stats` - Get user statistics

  1. Generate summary (once at end)- `POST /api/clear-session` - Clear session data

  2. Generate recommendations (once at end)

- No rate limiting concerns during question flow### Web Routes

- Fallback to basic text if API unavailable

- `GET /` - Home page

## Adding New Questions- `GET /assessment/start` - Start assessment form

- `POST /assessment/start` - Create new assessment

### Manual Addition- `GET /assessment/question` - Display current question

1. Edit `questions.json`- `POST /assessment/question` - Submit answer

2. Add questions to appropriate `domain_difficulty` array- `GET /assessment/results` - View results

3. Follow exact format (see example above)- `GET /dashboard/` - Dashboard overview

4. Restart application to reload questions

## 🔧 Configuration

### Bulk Generation

Use the Gemini website with `GEMINI_PROMPT_FOR_QUESTIONS.md` prompt (in Prototype2) to generate questions, then:### Environment Variables

1. Copy generated JSON

2. Validate format with `validate_questions.py` (in Prototype2)| Variable | Description | Default |

3. Merge into `questions.json`| ---------------- | --------------------- | ------------ |

4. Restart application| `GOOGLE_API_KEY` | Google Gemini API key | Required |

| `SECRET_KEY` | Flask secret key | Required |

## Benefits of Prototype3| `DEBUG` | Debug mode | `False` |

| `SESSION_TYPE` | Session storage type | `filesystem` |

### Advantages| `FLASK_ENV` | Flask environment | `production` |

✅ **No quota concerns** - unlimited assessments without API limits

✅ **Faster question loading** - instant, no API delays ### Debug Mode

✅ **More predictable** - questions are reviewed and validated

✅ **Offline capability** - works without internet (except for results AI) Enable comprehensive debugging:

✅ **Cost-effective** - minimal API usage (2 calls per assessment)

✅ **Easier maintenance** - questions in one file ```python

DEBUG=True # In .env file

### Trade-offs```

⚠️ **Manual question creation** - need to populate questions.json manually

⚠️ **No question variety** - limited to hardcoded questions Features when enabled:

⚠️ **Storage requirements** - large JSON file (but manageable)

- Detailed error pages

## Logging- Debug info panel in templates

- Auto-reload on code changes

Application logs show:- Verbose logging to console and file

- Question bank loading stats

- Question selection (domain, difficulty)## 📊 Logging

- AI summary/recommendation generation

- Assessment progressLogs are written to:

- Error details

- **Console**: All log levels when `DEBUG=True`

Example startup logs:- **File**: `logs/app.log` (auto-created)

````

2024-01-01 12:00:00 - INFO - 🚀 Loading hardcoded question bank...Log format:

2024-01-01 12:00:01 - INFO - ✅ Question bank loaded: 900 total questions

2024-01-01 12:00:01 - INFO -    network-security: 300 questions (100 beginner, 100 intermediate, 100 advanced)```

2024-01-01 12:00:01 - INFO -    secure-coding: 300 questions (100 beginner, 100 intermediate, 100 advanced)2024-01-15 10:30:45 - gemini_service - DEBUG - Generating question for domain: network-security

2024-01-01 12:00:01 - INFO -    incident-response: 300 questions (100 beginner, 100 intermediate, 100 advanced)```

````

## 🎨 Frontend

## Testing

- **Framework**: Tailwind CSS (CDN)

### Manual Testing- **Icons**: Heroicons (SVG)

1. Start assessment with different domains- **Animations**: CSS transitions and fade-in effects

2. Answer questions (verify random selection)- **Responsive**: Mobile-first design

3. Complete assessment (verify AI summary/recommendations)- **Theme**: Dark mode with cyan/blue accents

4. Start new assessment (verify question reset works)

## 🐛 Debugging Tips

### Validation

```bash1. **Check Logs**: Review `logs/app.log` for detailed errors

# Verify questions.json format2. **Debug Panel**: Enable in templates to see route/session info

python -c "import json; json.load(open('questions.json')); print('✅ Valid JSON')"3. **API Health**: Test with `curl http://localhost:5000/api/health`

4. **Session Data**: Check `flask_session/` directory

# Count questions5. **Environment**: Verify `.env` file has correct API key

python -c "import json; d=json.load(open('questions.json')); print(f'Total: {sum(len(v) for v in d[\"questions\"].values())}')"

```## 📝 Development



## Troubleshooting### Adding a New Domain



### Issue: "No questions available"1. Update `assessment_service.py` with domain details

- **Solution**: Check `questions.json` exists and has questions for the selected domain/difficulty2. Add domain card to `templates/home.html`

- **Check**: Run `question_bank.get_question_count()` to see available questions3. Add domain icon to `templates/dashboard/index.html`



### Issue: AI summary not generating### Adding a New Route

- **Solution**: Check `GEMINI_API_KEY` in `.env`

- **Fallback**: System will show basic summary without AI1. Create blueprint in `routes/` directory

2. Register in `app.py`

### Issue: Questions repeating3. Create corresponding template in `templates/`

- **Solution**: Call `question_bank.reset_used_questions()` or restart application

- **Note**: Questions are tracked per domain/difficulty to avoid repeats within session### Modifying AI Prompts



## Future EnhancementsEdit prompts in `services/gemini_service.py`:



Potential improvements:- `generate_question()` - Question generation prompt

- Question difficulty rating based on user performance- `generate_feedback()` - Feedback generation prompt

- Question tagging for targeted practice

- Export/import question banks## 🚧 Troubleshooting

- Question editing UI

- Analytics on question difficulty### Common Issues

- Multi-language support

**White screen / no questions:**

## Migration from Prototype2

- Check API key in `.env`

If migrating from Prototype2:- Review logs for Gemini API errors

1. Export questions from MySQL (if any)- Verify internet connection

2. Format as JSON following Prototype3 format

3. Copy `questions.json` to Prototype3 root**Session errors:**

4. Update `.env` (remove MySQL config)

5. Test question loading- Clear `flask_session/` directory

- Restart application

## License- Check file permissions



Same as parent project.**Import errors:**


- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## 📄 License

This project is part of a hackathon prototype.

## 🙏 Acknowledgments

- **Google Gemini AI**: Question and feedback generation
- **Flask**: Web framework
- **Tailwind CSS**: UI framework
- **Heroicons**: Icon library

---

**Built for HackathonEU** - Modular, AI-driven, and debugger-friendly! 🚀
```
