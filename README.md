Updated API for Future Prospects, much more Request Based and a lot more updated for more finalized function

HOW TO BE USED IN FUTURE:
run this constantly in other files, will check to see if API has updated info from user, will run based off that. Good for local offline running.
while True:
    if os.path.exists("translation_input.json"):
        data = json.load(open("translation_input.json"))
        result = process_translation(data)
        requests.post(API_URL + "/translation_to_backend", json=result)
        os.remove("translation_input.json")
