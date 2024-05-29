import time
import requests
import sys

HOST = "https://api.discogs.com"
USER_AGENT = "UniversityCourse/1.5"


def check_response(artistId):
    res = requests.get(HOST + f'/artists/{artistId}', headers={"User-Agent": USER_AGENT})
    while res.status_code == 429:
        print("Too many requests, sleeping for 1 minute...")
        time.sleep(61)
        res = requests.get(HOST + f'/artists/{artistId}', headers={"User-Agent": USER_AGENT})

    if res.status_code != 200:
        print("\tRequest error")
        print("\t", res.status_code, res.reason)
        sys.exit(1)

    try:
        data = res.json()
    except requests.exceptions.RequestException as e:
        print("\tRequest error")
        print("\tResponse didn't contain valid json")
        print("\t" + e.__class__.__name__)
        sys.exit(1)

    # Sytuacja gdy id nalezy do zespołu a nie osoby
    if "groups" not in data:
        print("Provided id must be assigned to a person:")
        print(f'\t{data["id"]}\t{data["name"]}')
        sys.exit(1)

    return data


def main():
    groups = {}

    if len(sys.argv) < 3:
        print("Usage: python " + sys.argv[0] + " artist1Id" + " artist2Id" + " ...")
        print("You must provide at least 2 artists' id ")
        sys.exit(1)

    for artistId in sys.argv[1:]:
        print('Check for id: ' + artistId + '...')
        json = check_response(artistId)
        print("\tArtist's name: " + json['name'])

        # print("\tArtist's groups: ")
        for group in json["groups"]:
            # print("\t\t" + group['name'])
            groups[group['name']] = {*groups.get(group['name'], set()), json['name']}

    print('\nMatching groups: ')
    for key in sorted(filter(lambda x: len(groups[x]) > 1, groups.keys())):  # grupy są posortowanie alfabetycznie
        print("\t" + key + ": " + str(len(groups[key])))
        for person in groups[key]:
            print("\t\t" + person)


if __name__ == "__main__":
    main()
