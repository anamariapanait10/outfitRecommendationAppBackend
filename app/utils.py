import json
from openai import OpenAI

client = OpenAI()

def find_substring(main_string, string_list):
    for substring in string_list:
        if substring.lower() in main_string.lower():
            return substring
    return None

def get_classification_from_gpt(image):
    prompt = (
                "Classify this clothing item by color (one of 'white','beige','black','light gray','gray','dark gray','yellow','dark yellow','light green','green','dark green',"
                "'turquoise','orange','light blue','blue','dark blue','light pink','pink','red','dark red','brown','purple','multicolor'),"
                "pattern (one of 'Striped','Checkered','Floral','Dotted','Plain','Animal print','Camouflage','Graphic']), material (one of ['Cotton','Wool','Silk','Synthetic fibers','Leather','Linen'])"
                " and by the best occasion where it could be worn, named occasion in the json (one of ['Casual', 'Ethnic', 'Formal', 'Sports', 'Smart Casual', 'Party'])."
                " Also add the following fields: temperature (numeric value representing the optimal temperature for wearing the clothing item),"
                " weather (the optimal weather for wearing the clothing item, should be one of 'snowy', 'rainy', 'overcast', 'sunny'),"
                " preference (a decimal value between 0 and 1 representing a subjective stylistic preference of wearing this clothing item, don't be afraid to judge harshly). Return answer in json format"
            )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image,
                            "detail": "low"
                        },
                    },
                ],
            }
        ],
        max_tokens=150,
    )

    response = response.choices[0].message.content
    response = json.loads(response.replace('```json', '').replace('```', ''))
    return response