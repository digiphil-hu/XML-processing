import json


def create_json_data(input_dict, output_path):
    initial_json = {
        "access": {
            "files": "public",
            "record": "public"
        },
        "files": {"enabled": True},
        "metadata": {"contributors": [],
                     "creators": []
                     },
        "pids": {}
    }
    json_data = initial_json

    # Add creators
    creators = input_dict["Creators"]
    for creator in creators:
        json_data = add_creator(json_data, creator)

    # Add contributors
    contributors = input_dict["Contributors"]
    for contributor in contributors:
        json_data = add_contributor(json_data, contributor)

    # Write json to path
    file_name = input_dict['filename'].replace(".xml", ".json")
    write_json(json_data, (output_path + "/" + file_name))


def add_creator(existing_data, creator_data_list):

    # Add creator to the "creators" list
    # If there is an identifier:
    if len(creator_data_list) > 3:
        creator_id = creator_data_list[3].split(':')[1].strip()
        creator_id_scheme = creator_data_list[3].split(':')[0].strip()

        existing_data["metadata"]["creators"].append({
            "person_or_org": {
                "family_name": creator_data_list[0],
                "given_name": creator_data_list[1],
                "identifiers": [
                    {
                        "identifier": creator_id,
                        "scheme": creator_id_scheme
                    }
                ],
                "name": f"{creator_data_list[0]}, {creator_data_list[1]}",
                "type": "personal"
            },
            "role": {
                "id": creator_data_list[2].lower(),
                "title": {
                    "en": creator_data_list[2]
                }
            }
        })
    else:
        existing_data["metadata"]["creators"].append({
            "person_or_org": {
                "family_name": creator_data_list[0],
                "given_name": creator_data_list[1],
                "identifiers": [],
                "name": f"{creator_data_list[0]}, {creator_data_list[1]}",
                "type": "personal"
            },
            "role": {
                "id": creator_data_list[2].lower(),
                "title": {
                    "en": creator_data_list[2]
                }
            }
        })
    return existing_data


def add_contributor(existing_data, contributor_data_list):
    # Add contributor to the "contributors" list
    existing_data["metadata"]["contributors"].append({
        "person_or_org": {
            "family_name": contributor_data_list[0],
            "given_name": contributor_data_list[1],
            "identifiers": [
                # {
                #     "identifier": contributor_data_list[x],
                #     "scheme": contributor_data_list[x]
                # }
            ],
            "name": f"{contributor_data_list[0]}, {contributor_data_list[1]}",
            "type": "personal"
        },
        "role": {
            "id": contributor_data_list[2].lower(),
            "title": {
                "en": contributor_data_list[2]
            }
        }
    })
    return existing_data


def write_json(json_data, path):
    # Write data to a JSON file
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=2)
