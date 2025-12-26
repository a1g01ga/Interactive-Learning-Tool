# Interactive Learning Tool (SAE 3.5)

A simple, menu‑driven CLI app to create, practice, test, and manage study questions. It can generate new questions with
an LLM, track your performance, and bias practice toward items you miss more often.

## Project Overview

- Generate Questions: Use an LLM to create MCQ and freeform questions for a topic you choose, review them, and save the
  ones you accept.
- Practice Mode: Repeated practice of active questions; items you’ve missed appear more often via weighted selection.
- Test Mode: Take a test with a chosen number of non‑repeating questions; a score is saved to data/results.txt.
- Statistics: View question stats (active status, type, times shown, and correctness%).
- Manage Questions: List and enable/disable questions by ID.

## Installation

Python 3.10+ is recommended.

Choose one of the following:

- pip
  ```bash
  pip install -r requirements.txt
  ```
- uv
  ```bash
  uv pip install -r requirements.txt
  ```

## Configuration

The app uses environment variables (loaded via python-dotenv if you have a .env file):

- OPENAI_API_KEY: required for LLM features
- OPENAI_MODEL: optional model name (default: gpt-4o)

Create a .env file in the project root, for example:

```env
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o
```

## Usage

From the project root:

```bash
python main.py
```

Follow the on-screen menu to select a mode:

1. Generate Questions Mode
2. Statistics Viewing Mode
3. Manage Questions Mode
4. Practice Mode
5. Test Mode

## Features

- Separate menu items for each major function
- Weighted practice selection that emphasizes questions you answered incorrectly more often
- Random, no-repetition test selection
- MCQ local evaluation and LLM-backed freeform evaluation
- Persistent storage of questions and test results

## Data Files

- data/questions.json: stored questions
- data/results.txt: appended test scores with timestamps

## Running Tests

Using pytest:

```bash
pytest -q
```

## Notes for Developers

- Core modules:
    - core/question.py: base Question plus MCQQuestion and FreeformQuestion
    - core/quiz_manager.py: loading/saving and basic CRUD/metrics
    - core/selector.py: weighted choice (practice) and random unique sampling (test)
    - core/evaluator.py: MCQ evaluation locally; freeform via llm/llm_client.py
    - persistence/file_handler.py: JSON/TXT I/O helpers
- Prompts in prompts/*.j2 guide question generation and evaluation.
- Configuration in config.py reads environment with python-dotenv.

## Troubleshooting

- Missing API key: Set OPENAI_API_KEY in your environment or .env; LLM features will not work without it.
- Network/Quota errors: The app surfaces basic OpenAI SDK errors and continues without crashing; try again later or
  check your key/limits.

---
See my other projects: https://github.com/olga0011 