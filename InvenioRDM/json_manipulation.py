import json


def parse_input_json(path_in):

    # Read existing JSON data
    try:
        with open(path_in, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error reading {path_in}. Make sure the file exists and contains valid JSON.")
        return
    return existing_data


def add_contributor(existing_data, contributor_data_list):

    # Add contributor to the "contributors" list
    existing_data["metadata"]["contributors"].append({
        "person_or_org": {
            "family_name": contributor_data_list[0],
            "given_name": contributor_data_list[1],
            "identifiers": [
                {
                    "identifier": contributor_data_list[2],
                    "scheme": contributor_data_list[3]
                }
            ],
            "name": f"{contributor_data_list[0]}, {contributor_data_list[1]}",
            "type": "personal"
        },
        "role": {
            "id": contributor_data_list[4],
            "title": {
                "en": contributor_data_list[5]
            }
        }
    })
    return existing_data


def change_PID(existing_data, change_value_to_string):
    try:
        # Locate the second [identifier] under [metadata][related_identifiers]
        identifier_to_change = existing_data["metadata"]["related_identifiers"][1]["identifier"]

        # Change the value to the provided string
        existing_data["metadata"]["related_identifiers"][1]["identifier"] = (identifier_to_change +
                                                                             change_value_to_string)

        print(f"Changed the value of the second [identifier] to: {change_value_to_string}")

    except (KeyError, IndexError) as e:
        print(f"Error: {e}")
    return existing_data


def write_json(existing_data, path):

    # Write the updated data back to the JSON file
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=2)


if __name__ == '__main__':

    # Specify the input and the output file path
    input_file_path, output_file_path = ("record.json", "output.json")

    #PID
    PID = "rmkt-17-6.tei.19"

    # Contributor data to add [family_name, given_name, identifier, scheme, role_id, role_en]
    contributor_data = ["Doe", "John", "123456789", "orcid", "editor", "Editor"]

    # Parse the input file and add a contributor to the existing JSON
    input_data = parse_input_json(input_file_path)
    output_data = add_contributor(input_data, contributor_data)
    output_data = change_PID(output_data, PID)
    write_json(output_data, output_file_path)
    print("Output written to {}".format(output_file_path))


