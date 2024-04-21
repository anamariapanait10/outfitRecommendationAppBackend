#for color classification
import colorsys                                                     
import PIL.Image as Image
from io import BytesIO
import base64
import re
from scipy.spatial import KDTree
from webcolors import (
   CSS3_HEX_TO_NAMES,
    hex_to_rgb
)

# Expanded mapping for CSS color names to broader categories
color_to_category_mapping = {
    'aliceblue': 'white',
    'antiquewhite': 'beige',
    'aqua': 'turquoise',
    'aquamarine': 'turquoise',
    'azure': 'white',
    'beige': 'beige',
    'bisque': 'beige',
    'black': 'black',
    'blanchedalmond': 'beige',
    'blue': 'blue',
    'blueviolet': 'purple',
    'brown': 'brown',
    'burlywood': 'beige',
    'cadetblue': 'dark-green',
    'chartreuse': 'light-green',
    'chocolate': 'orange',
    'coral': 'orange',
    'cornflowerblue': 'light-blue',
    'cornsilk': 'light-gray',
    'crimson': 'dark-red',
    'cyan': 'turquoise',
    'darkblue': 'blue',
    'darkcyan': 'dark-green',
    'darkgoldenrod': 'dark-yellow',
    'darkgray': 'dark-gray',
    'darkgreen': 'dark-green',
    'darkkhaki': 'dark-green',
    'darkmagenta': 'purple',
    'darkolivegreen': 'dark-green',
    'darkorange': 'orange',
    'darkorchid': 'purple',
    'darkred': 'dark-red',
    'darksalmon': 'pink',
    'darkseagreen': 'light-green',
    'darkslateblue': 'dark-blue',
    'darkslategray': 'dark-gray',
    'darkturquoise': 'turquoise',
    'darkviolet': 'purple',
    'deeppink': 'pink',
    'deepskyblue': 'light-blue',
    'dimgray': 'gray',
    'dodgerblue': 'blue',
    'firebrick': 'dark-red',
    'floralwhite': 'white',
    'forestgreen': 'green',
    'fuchsia': 'pink',
    'gainsboro': 'light-gray',
    'ghostwhite': 'light-gray',
    'gold': 'yellow',
    'goldenrod': 'yellow',
    'gray': 'gray',
    'green': 'green',
    'greenyellow': 'light-green',
    'honeydew': 'white',
    'hotpink': 'pink',
    'indianred': 'red',
    'indigo': 'purple',
    'ivory': 'white',
    'khaki': 'yellow',
    'lavender': 'light-pink',
    'lavenderblush': 'light-pink',
    'lawngreen': 'light-green',
    'lemonchiffon': 'beige',
    'lightblue': 'light-blue',
    'lightcoral': 'red',
    'lightcyan': 'light-blue',
    'lightgoldenrodyellow': 'beige',
    'lightgreen': 'light-green',
    'lightgrey': 'light-gray',
    'lightpink': 'pink',
    'lightsalmon': 'orange',
    'lightseagreen': 'turquoise',
    'lightskyblue': 'light-blue',
    'lightslategray': 'gray',
    'lightsteelblue': 'light-blue',
    'lightyellow': 'yellow',
    'lime': 'green',
    'limegreen': 'green',
    'linen': 'beige',
    'magenta': 'purple',
    'maroon': 'dark-red',
    'mediumaquamarine': 'green',
    'mediumblue': 'blue',
    'mediumorchid': 'purple',
    'mediumpurple': 'purple',
    'mediumseagreen': 'green',
    'mediumslateblue': 'purple',
    'mediumspringgreen': 'green',
    'mediumturquoise': 'turquoise',
    'mediumvioletred': 'pink',
    'midnightblue': 'dark-blue',
    'mintcream': 'white',
    'mistyrose': 'pink',
    'moccasin': 'beige',
    'navajowhite': 'beige',
    'navy': 'dark-blue',
    'oldlace': 'beige',
    'olive': 'green',
    'olivedrab': 'green',
    'orange': 'orange',
    'orangered': 'orange',
    'orchid': 'purple',
    'palegoldenrod': 'yellow',
    'palegreen': 'light-green',
    'paleturquoise': 'turquoise',
    'palevioletred': 'pink',
    'papayawhip': 'beige',
    'peachpuff': 'orange',
    'peru': 'brown',
    'pink': 'pink',
    'plum': 'pink',
    'powderblue': 'light-blue',
    'purple': 'purple',
    'red': 'red',
    'rosybrown': 'brown',
    'royalblue': 'blue',
    'saddlebrown': 'brown',
    'salmon': 'pink',
    'sandybrown': 'orange',
    'seagreen': 'green',
    'seashell': 'white',
    'sienna': 'brown',
    'silver': 'light-gray',
    'skyblue': 'light-blue',
    'slateblue': 'blue',
    'slategray': 'gray',
    'snow': 'white',
    'springgreen': 'green',
    'steelblue': 'blue',
    'tan': 'orange',
    'teal': 'dark-green',
    'thistle': 'purple',
    'tomato': 'red',
    'turquoise': 'turquoise',
    'violet': 'purple',
    'wheat': 'beige',
    'white': 'white',
    'whitesmoke': 'white',
    'yellow': 'yellow',
    'yellowgreen': 'light-green',
}

def convert_rgb_to_names(rgb_tuple):
    # a dictionary of all the hex and their respective names in css3
    css3_db = CSS3_HEX_TO_NAMES
    names = []
    rgb_values = []
    for color_hex, color_name in css3_db.items():
        names.append(color_name)
        rgb_values.append(hex_to_rgb(color_hex))
    
    kdt_db = KDTree(rgb_values)
    distance, index = kdt_db.query(rgb_tuple)
    return names[index]


def get_cloth_color(image):
    max_score = 0.0001
    dominant_color = None
    for count,(r,g,b) in image.getcolors(image.size[0]*image.size[1]):
       
        saturation = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)[1]
        y = min(abs(r*2104+g*4130+b*802+4096+131072)>>13,235)
        y = (y-16.0)/(235-16)
        if y > 0.9:
            continue
        score = (saturation+0.1)*count
        if score > max_score:
            max_score = score
            dominant_color = (r,g,b)
            
    return convert_rgb_to_names(dominant_color)
 
    
def color_classification(single_path):
    image = Image.open(single_path)
    image = image.convert('RGB')
    category = color_to_category_mapping.get(get_cloth_color(image), "No category found")
    return category

def color_classification_b64(b64_image):
    b64_image = re.sub('^data:image/.+;base64,', '', b64_image)
    image = Image.open(BytesIO(base64.b64decode(b64_image)))
    
    image = image.convert('RGB')
    category = color_to_category_mapping.get(get_cloth_color(image), "No category found")
    return category

