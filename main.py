from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import time
import os

app = FastAPI(
    title="Codex Middleware Translation Request API",
    description="Handles JSON passing between Frontend -> Translation Program -> Medication Database -> Frontend.",
    version="1.0"
)

# JSONs for INPUT/OUTPUT inbetween teams

TRANSLATION_INPUT = "translation_input.json"
TRANSLATION_OUTPUT = "translation_output.json"

BACKEND_INPUT = "lookup_input.json"
BACKEND_OUTPUT = "lookup_output.json"


#Models for initial input and final output

class UserInput(BaseModel):
    original_language: str
    requested_language: str
    original_medication: str


class FinalOutput(BaseModel):
    original_language: str
    requested_language: str
    original_medication: str
    translated_medication: str
    medication_matches: list


#Helper functions

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

#Wait function for time between responses othherwise timeout
def wait_for_json(path, timeout=10):
    start = time.time()
    while not os.path.exists(path):
        if time.time() - start > timeout:
            raise TimeoutError(f"Timed out waiting for {path}")
        time.sleep(0.1)
    return read_json(path)

#Sarting Point
@app.post("/process", response_model=FinalOutput)
def process_medication(data: UserInput):

    # Ensures the Original Request has filled out fields
    # Expected Fields: original_language, requested_language, original_medication
    if not data.original_language.strip():
        raise HTTPException(400, "Original language cannot be empty")

    if not data.requested_language.strip():
        raise HTTPException(400, "Requested language cannot be empty")

    if not data.original_medication.strip():
        raise HTTPException(400, "Original medication cannot be empty")

    # Reformats and sets standard for json input/output
    translation_input = {
        "original_language": data.original_language.strip(),
        "requested_language": data.requested_language.strip(),
        "original_medication": data.original_medication.strip()
    }

    write_json(TRANSLATION_INPUT, translation_input)

    # Waits for translation output
    try:
        translation_output = wait_for_json(TRANSLATION_OUTPUT)
    except TimeoutError as e:
        raise HTTPException(500, str(e))

    #

    # Unsupported language Error
    if "supported" in translation_output and translation_output["supported"] is False:
        message = translation_output.get("message", "Unsupported Language")
        raise HTTPException(400, f"Translation error: {message}")

    # Missing Translation Error
    translated_medication = translation_output.get("translated_medication")
    if not translated_medication:
        raise HTTPException(500, "Translation program did not return a translated medication")

    # Cleans up the Translation json, removing any unnecessary verification info
    cleaned_translation = {
        "translated_medication": translated_medication.strip(),
        "requested_language": data.requested_language,
        "original_medication": data.original_medication,
    }

    write_json(BACKEND_INPUT, cleaned_translation)

    #Waits for Database lookup
    try:
        lookup_output = wait_for_json(BACKEND_OUTPUT)
    except TimeoutError as e:
        raise HTTPException(500, str(e))

    #Database Verifications

    # No Medications found Error
    if lookup_output.get("success") is False:
        raise HTTPException(404, "No matching medications found in database")

    # Error in Medication list output, success flag but empty data
    matches = lookup_output.get("matches")
    if matches is None:
        raise HTTPException(500, "Medication lookup program returned invalid data")

    # Cleans up final response
    final_matches = [
        {
            "generic": m.get("generic"),
            "brand": m.get("brand")
        }
        for m in matches
    ]

    # Final Return
    return {
        "original_language": data.original_language,
        "requested_language": data.requested_language,
        "original_medication": data.original_medication,
        "translated_medication": translated_medication,
        "medication_matches": final_matches
    }