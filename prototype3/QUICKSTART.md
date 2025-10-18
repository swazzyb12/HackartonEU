# Prototype3 Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd prototype3
pip install -r requirements.txt
```

### 2. Configure Gemini API

Create `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=dev-secret-key-123
FLASK_DEBUG=True
```

### 3. Run Application

```bash
python app.py
```

Open http://localhost:5000

## How It Works

### Question Flow (No AI)

1. Select domain (network-security, secure-coding, incident-response)
2. Questions loaded from `questions.json`
3. Random unused questions selected
4. Adaptive difficulty based on performance

### AI Features (End of Assessment)

1. Personalized summary of performance
2. Specific learning recommendations
3. Only 2 API calls per assessment

## Testing

### Quick Test

```bash
# Test question loading
python -c "from services import QuestionBank; qb = QuestionBank(); print(f'Loaded {qb.get_question_count()[\"total\"]} questions')"

# Start the app
python app.py
```

### Full Test

1. Start assessment: http://localhost:5000
2. Select "Network Security" domain
3. Answer 10 questions
4. View results with AI summary

## Current Question Bank

**Total Questions: 81**

- Network Security: 23 questions
- Secure Coding: 29 questions
- Incident Response: 29 questions

### Distribution by Difficulty

- Beginner: ~27 questions
- Intermediate: ~27 questions
- Advanced: ~27 questions

## Adding Questions

### Manual Method

1. Open `questions.json`
2. Find the appropriate category (e.g., `network-security_beginner`)
3. Add question in this format:

```json
{
  "title": "Question Title",
  "question": "Full question text?",
  "domain": "network-security",
  "difficulty": "beginner",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct": 0,
  "explanation": "Explanation of the correct answer",
  "learningPoints": ["Key learning point 1", "Key learning point 2"],
  "sources": ["https://source-url.com"]
}
```

4. Restart application

### Bulk Generation (using Gemini website)

1. Go to gemini.google.com
2. Use prompt from `../Prototype2/GEMINI_PROMPT_FOR_QUESTIONS.md`
3. Generate 10-100 questions
4. Copy JSON output
5. Validate: `python ../Prototype2/validate_questions.py`
6. Merge into `questions.json`
7. Restart application

## Architecture

```
prototype3/
├── questions.json                # 📦 Hardcoded question bank
├── app.py                        # 🚀 Flask application
├── services/
│   ├── question_bank.py          # 📚 Load & select questions
│   ├── gemini_service.py         # 🤖 AI summaries only
│   └── assessment_service.py     # 📊 Scoring & tracking
├── routes/
│   └── assessment.py             # 🛣️ Assessment flow
└── templates/
    └── assessment/               # 🎨 UI templates
```

## Key Benefits

✅ **Fast** - No AI delays during questions  
✅ **Reliable** - No rate limits or quota issues  
✅ **Offline** - Works without internet (except AI summaries)  
✅ **Cost-effective** - Minimal API usage  
✅ **Predictable** - Reviewed questions only

## Troubleshooting

### "No questions available"

```bash
# Check questions.json exists
ls questions.json

# Verify it's valid JSON
python -c "import json; json.load(open('questions.json'))"

# Count questions
python -c "from services import QuestionBank; print(QuestionBank().get_question_count())"
```

### AI summary not working

```bash
# Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

### Questions repeating

- Questions are tracked per session
- Restart app to reset tracking
- Or implement reset button in UI

## Next Steps

1. **Add more questions** - Aim for 100+ per domain/difficulty
2. **Test all domains** - Ensure variety
3. **Collect feedback** - See if difficulty is appropriate
4. **Enhance AI summaries** - Tune prompts for better feedback

## Comparison to Prototype2

| Feature         | Prototype2        | Prototype3              |
| --------------- | ----------------- | ----------------------- |
| Question Source | AI generated      | Hardcoded JSON          |
| API Calls       | Every question    | Only at end             |
| Speed           | Slower (AI wait)  | Instant                 |
| Cost            | Higher            | Minimal                 |
| Flexibility     | Unlimited variety | Limited to bank         |
| Reliability     | Rate limits       | 100% reliable           |
| Offline         | No                | Yes (except AI summary) |

## Ready to Deploy?

See `README.md` for complete documentation.

Questions? Check the logs in `debug.log`.
