import re
from os import walk
from pygame.image import load

def import_data(path):
    images_tab = []
    for _, _, files in walk(path):
        for file in files:
            image_path = path + "/"+ file
            image = load(image_path).convert_alpha()
            images_tab.append(image)
    return images_tab


def import_data_dict(path):
    images_dict = {}
    for _, _, files in walk(path):
        for file in files:
            image_path = path + "/"+ file
            name = file.split('.')[0]
            image = load(image_path).convert_alpha()
            images_dict[name] = image
    return images_dict


def import_data_folder_dict(path):
    images_dict = {}
    for _, dirnames, files in walk(path):
        if dirnames:
            for dirname in dirnames:
                images_dict[dirname] = import_data(path + "/" + dirname)
            for file in files:
                image_path = path + "/"+ file
                name = file.split('.')[0]
                if file != '.DS_Store':
                    image = load(image_path).convert_alpha()
                    images_dict[name] = image
    return images_dict


def save_txt(path, data):
    with open(path, 'w') as file:
        for key, value in data.items():
            file.write(f"{key}: {value}\n")


def load_settings(file_path):
    data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                # Format: key: bool
                match_boolean = re.match(r'(\w+):\s(True|False)', line)
                if match_boolean:
                    key = match_boolean.group(1)
                    value_str = match_boolean.group(2)
    
                    # Convert the string value to a boolean
                    value = value_str.lower() == 'true'
                    data[key] = value
    except FileNotFoundError:
        pass
    return data

def load_txt(file_path):
    data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                # Format: key: (x, y)
                match_tuple = re.match(r'(\w+): \((\d+), (\d+)\)', line)
                if match_tuple:
                    key, x, y = match_tuple.groups()
                    data[key] = (int(x), int(y))
                    continue

                # Format: key: { ... }
                match_dict = re.match(r'(.+?):\s*\{(.*)\}', line)
                if match_dict:
                    key, dict_content = match_dict.groups()

                    pattern = r"\((\d+),\s(\d+)\):\s(\d+|'[^']*')"
                    # Recherche de tous les matches dans le contenu
                    matches = re.findall(pattern, dict_content)

                    # Affichage des résultats
                    for match in matches:
                        x, y, value = match
                        value = int(value) if value.isdigit() else value.strip("'")
                        
                        if key in data:
                            data[key][int(x), int(y)] = value
                        else:
                            data[key] = {(int(x), int(y)): value}
    except FileNotFoundError:
        pass
    return data
