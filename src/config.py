from dotenv import find_dotenv, load_dotenv
import os
import json

# load_dotenv(find_dotenv())
load_dotenv(find_dotenv(), override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NO_GENERATED_SAMPLES = 10

LLM_TEMPERATURE = 1.0

MODEL_NAME = "gpt-4o"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TRAINING_FOLDER_PATH = os.path.join(BASE_DIR, "hmms", "training")

TRAINING_DATA_FOLDER_PATH = os.path.join(TRAINING_FOLDER_PATH, "data")

TRAINING_FILES = ["data.json", "actions.json", "durations.json", "preferences.json", "sentences.json"]


if not os.path.exists(TRAINING_FOLDER_PATH):
    os.makedirs(TRAINING_FOLDER_PATH)

if not os.path.exists(TRAINING_DATA_FOLDER_PATH):
    os.makedirs(TRAINING_DATA_FOLDER_PATH)

for file in TRAINING_FILES:
    if not os.path.exists(os.path.join(TRAINING_DATA_FOLDER_PATH, file)):
        with open(os.path.join(TRAINING_DATA_FOLDER_PATH, file), "w") as f:
            json.dump([], f)

# This will be a set of common actions, durations, preferences, and sentences on which we want to train the model
ACTIONS = json.load(open(os.path.join(TRAINING_DATA_FOLDER_PATH, "actions.json")))

DURATIONS = json.load(open(os.path.join(TRAINING_DATA_FOLDER_PATH, "durations.json")))

PREFERENCES = json.load(open(os.path.join(TRAINING_DATA_FOLDER_PATH, "preferences.json")))

SENTENCES = json.load(open(os.path.join(TRAINING_DATA_FOLDER_PATH, "sentences.json")))