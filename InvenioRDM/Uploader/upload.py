import requests
import json
import os


def main(records, token):
    # Create via https://127.0.0.1:5000/account/settings/applications/tokens/new/
    api = "https://invenio.abtk.hu/"
    # Define a list of records you want to upload:
    # ('<record metadata json>.json', ['<datafile1>', '<datafile2>'])
    # records = [
    #     ('rmkt-17-16.tei.ki-26.json', ['rmkt-17-16.tei.ki-26.xml', ])
    # ]
    #
    # HTTP Headers used during requests
    #
    h = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    fh = {
        "Accept": "application/json",
        "Content-Type": "application/octet-stream",
        "Authorization": f"Bearer {token}"
    }
    #
    # Upload and publish all records.
    #
    for datafile, files in records:
        # Load the record metadata JSON file.
        with open(datafile) as fp:
            data = json.load(fp)

        # Create the record
        # note: "verify=False" is so that we can connect to 127.0.0.1 with a
        # self-signed certificate. You should not do this in production.
        r = requests.post(
            f"{api}/api/records", data=json.dumps(data), headers=h, verify=False)
        assert r.status_code == 201, \
            f"Failed to create record (code: {r.status_code})"
        links = r.json()['links']

        # Upload files
        for f in files:
            # Initiate the file
            data = json.dumps([{"key": f}])
            r = requests.post(links["files"], data=data, headers=h, verify=False)
            assert r.status_code == 201, \
                f"Failed to create file {f} (code: {r.status_code})"
            file_links = r.json()["entries"][0]["links"]

            # Upload file content by streaming the data
            with open(f, 'rb') as fp:
                r = requests.put(
                    file_links["content"], data=fp, headers=fh, verify=False)
            assert r.status_code == 200, \
                f"Failed to upload file contet {f} (code: {r.status_code})"

            # Commit the file.
            r = requests.post(file_links["commit"], headers=h, verify=False)
            assert r.status_code == 200, \
                f"Failed to commit file {f} (code: {r.status_code})"

        # # Publish the record
        # r = requests.post( links["publish"], headers=h, verify=False)
        # assert r.status_code == 202, \
        #         f"Failed to publish record (code: {r.status_code})"


if __name__ == '__main__':
    path = "/home/pg/Documents/GitHub/XML-processing/InvenioRDM/Uploader"
    with open("token.txt", "r", encoding="utf8") as f:
        invenio_token = f.read().strip()
    for root, dirs, files in os.walk(path):
        for filenames in files:
            if filenames.endswith(".json"):
                filename_json = filenames
                filename_xml = filename_json.replace(".json", ".xml")
                if filename_xml not in files:
                    print(f"Uploading {filename_xml} failed.")
                    break

    for root, dirs, files in os.walk(path):
        for filenames in files:
            if filenames.endswith(".json"):
                filename_json = filenames
                filename_xml = filename_json.replace(".json", ".xml")
                metadata_and_file = [(filename_json, [filename_xml, ])]
                print(metadata_and_file)
                main(metadata_and_file, invenio_token)