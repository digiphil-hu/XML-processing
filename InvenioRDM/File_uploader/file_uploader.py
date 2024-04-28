import requests
import json
import os


def main(records, token):
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
    for invenio_key, files in records:
        # Load the record metadata JSON file.
        # with open(datafile) as fp:
        #     data = json.load(fp)

        # # Create a new version
        r = requests.post(
            f"{api}/api/records/{invenio_key}/versions", headers=h, verify=False)
        assert r.status_code == 201, \
            f"Failed to create record (code: {r.status_code})"
        new_version_json = r.json()
        new_key = new_version_json["links"]["self"].split("/")[-2]
        print(new_version_json)
        links = r.json()['links']
        print(new_key)

        # # Update publication date and version
        # data =
        # r = requests.put(
        #                 f"{api}/api/records/{new_key}/draft", data=data, headers=h, verify=False)
        # print(r.json)
        # assert r.status_code == 200, \
        #     f"Failed to update date (code: {r.status_code})"

        # Upload files
        for f in files:
            # Initiate the file
            data = json.dumps([{"key": f}])
            print(data, "\n", links["files"])
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
    path = "/home/pg/Documents/GitHub/XML-processing/InvenioRDM/File_uploader"
    invenio_key_and_file = [
                            ("vxd8n-wqf60", ["rmkt-17-6.tei.eloszo.xml", ])
                            ]
    with open("/home/pg/Documents/GitHub/XML-processing/InvenioRDM/Uploader/token.txt", "r", encoding="utf8") as f:
        invenio_token = f.read().strip()
        main(invenio_key_and_file, invenio_token)