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
        "Classify this clothing item by subcategory (one of 'T-shirt' (can be with short or long sleeves),'Polo Shirt','Shirt','Sweater','Jacket','Hoodie','Blazer','Jeans',"
        "'Track Pants','Shorts','Skirt','Leggings','Trousers','Dress','Bodysuit','Jumpsuit','Sneakers','Slippers','Sandals','Flats',"
        "'Sports Shoes','Heels','Hiking Shoes','Boots','Sandal Heels','Tie','Watch','Belt','Jewelry','Handbag','Backpack','Cap','Hat','Beanie'),"
        "seasons (one or multiple of 'Spring','Summer','Autumn','Winter', as a string separated with comma and without apostrophes or spaces),"
        "color (one of more of 'white','beige','black','light gray','gray','dark gray','yellow','dark yellow','light green','green','dark green',"
        "'turquoise','orange','light blue','blue','dark blue','light pink','pink','red','dark red','brown','purple','multicolor', as a string separated with comma and without apostrophes or spaces),"
        "pattern (one or more of 'Striped','Checkered','Floral','Dotted','Plain','Animal print','Camouflage','Graphic']),"
        "material (one of ['Cotton','Wool','Silk','Synthetic fibers','Leather','Linen'])"
        " and by the best occasion where it could be worn, named occasion in the json (one or more of ['Casual','Ethnic','Formal','Sports','Smart Casual','Party'], , as a string separated with comma and without apostrophes or spaces)."
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

def get_description_from_gpt(item):
    prompt = (
        f"Generate a short description (max 20 tokens) for the following clothing item that can be used to sell it in a marketplace(color {item.color},"
        f"subcategory {item.subCategory},pattern {item.pattern},material {item.material},"
        f"seasons {item.seasons},occasions {item.occasions}).Try to not repeat the information provided."
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
                            "url": item.image,
                            "detail": "low"
                        },
                    },
                ],
            }
        ],
        max_tokens=30,
    )

    response = response.choices[0].message.content
    print(response)
    # response = json.loads(response.replace('```json', '').replace('```', ''))
    return response