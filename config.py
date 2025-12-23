import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Project base directory (the package root)
BASE_DIR = os.path.dirname(__file__)

# Directories and paths
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
DATA_DIR = os.path.join(BASE_DIR, "data")
QUESTIONS_PATH = os.path.join(DATA_DIR, "questions.json")
RESULTS_PATH = os.path.join(DATA_DIR, "results.txt")

# Defaults for question generation
DEFAULT_NUM_MCQ = 3
DEFAULT_NUM_FREEFORM = 1
