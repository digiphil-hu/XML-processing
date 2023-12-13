import json


def create_json_data(input_dict, output_path):
    initial_json = {
        "access": {
            "files": "public",
            "record": "public"
        },
        "files": {"enabled": True},
        "metadata": {"contributors": [],
                     "creators": [],
                     "dates": [],
                     "description": "",
                     "identifiers": [],
                     "languages": [],
                     "publication_date": "",
                     "publisher": "",
                     "resource_type": {},
                     "related_identifiers": [],
                     "rights": [],
                     "subjects": [],
                     "title": "",
                     "version": ""
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

    # Add dates (like print publication)
    for date in input_dict["Dates"]:
        json_data = add_dates(json_data, date)

    # Add description
    json_data["metadata"]["description"] = input_dict["Description"]

    # Add alternative identifiers
    for identifier in input_dict["Alternate Identifiers"]:
        json_data = add_alternate_identifier(json_data, identifier)

    # Add languages
    for language in input_dict["Languages"]:
        json_data = add_language(json_data, language)

    # Add publication date
    json_data["metadata"]["publication_date"] = input_dict["publication_date"]

    # Add publisher
    json_data["metadata"]["publisher"] = input_dict["Publisher"]

    # Add resource type
    resource_type = input_dict["Resource type"]
    json_data["metadata"]["resource_type"] = {"id": resource_type.lower(), "title": {"en": resource_type}}

    # Add related identifiers
    for identifier in input_dict["Related works"]:
        json_data = add_related_identifier(json_data, identifier)

    # Add rights statements
    json_data["metadata"]["rights"] = [{"id": input_dict["Licenses"]}]

    # Add subjects
    for subject in input_dict["Subjects"]:
        json_data = add_subject(json_data, subject)

    # Add title
    json_data["metadata"]["title"] = input_dict["Title"]

    # Add version
    json_data["metadata"]["version"] = input_dict["Version"]

    # Write json to path
    file_name = input_dict['Filename'].replace(".xml", ".json")
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
                        "scheme": creator_id_scheme.lower()
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
        # No identifier
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
    # TODO: If a contributor has identifier!
    existing_data["metadata"]["contributors"].append({
        "person_or_org": {
            "family_name": contributor_data_list[0],
            "given_name": contributor_data_list[1],
            "identifiers": [
                {
                    "identifier": "",
                    "scheme": ""
                }
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


def add_dates(existing_data, date_data_list):
    # Add 'dates' field to json
    existing_data["metadata"]["dates"].append(
        {
            "date": date_data_list[0],
            "description": date_data_list[2],
            "type": {
                "id": date_data_list[1].lower(),
                "title": {
                    "en": date_data_list[1]
                }
            }
        })
    return existing_data


def add_alternate_identifier(existing_data, identifier_data):
    # Add alternate identifer (as Handle) to json
    existing_data["metadata"]["identifiers"].append(
        {
            "identifier": identifier_data[0],
            "scheme": identifier_data[1].lower()
        }
    )
    return existing_data


def add_language(existing_data, language_data):
    langugae_code = language_data.split(":")[0]
    language_in_english = language_data.split(":")[1]
    existing_data["metadata"]["languages"].append(
        {
            "id": langugae_code,
            "title": {
                "en": language_in_english
            }
        }
    )

    return existing_data


def add_related_identifier(existing_data, identifier):
    # Add an identifier
    existing_data["metadata"]["related_identifiers"].append(
        {
            "identifier": identifier[1],
            "relation_type": {
                "id": identifier[0].lower().replace(" ", ""),
                "title": {
                    "en": identifier[0]
                }
            },
            "resource_type": {
                "id": identifier[3].lower(),
                "title": {
                    "en": identifier[3]
                }
            },
            "scheme": identifier[2].lower()
        }
    )
    return existing_data


def add_subject(existing_data, subject):
    existing_data["metadata"]["subjects"].append({"subject": subject})
    return existing_data


def write_json(json_data, path):
    # Write data to a JSON file
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=2)
