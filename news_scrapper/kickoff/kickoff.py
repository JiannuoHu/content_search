import json

def kickoff(event, context):

    # website_names = ['reuters', 'nyt','wsj','themiddlemarket']
    website_names = ['reuters', 'nyt','wsj']

    with open("elephants.json") as f:
        elephants = json.load(f)
    
    input_list = [{'website': web, "elephants":elephants} for web in website_names]

    return input_list