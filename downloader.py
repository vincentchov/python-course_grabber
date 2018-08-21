import json
import pathlib
from urllib.request import urlretrieve


def clean_filename(filename):
    """ Replaces illegal characters from filenames with underscores. """
    keep_chars = (' ', '.', '_', '-')
    chars = [c if c.isalnum() or c in keep_chars else '_' for c in filename]
    return "".join(chars).rstrip()


def download_all_videos(list_of_lectures, dest_folder):
    """ Takes the JSON and runs wget on all of the links. """
    pathlib.Path(dest_folder).mkdir(parents=True, exist_ok=True)
    length = len(list_of_lectures)
    i = 1
    for pair in list_of_lectures:
        filename = "{}.mp4".format(clean_filename(pair[0]))
        url = pair[1]
        print("({}/{}) Downloading '{}' as '{}'".format(i, length,
                                                        pair[0], filename))
        urlretrieve(url, "{}/{}".format(dest_folder, filename))
        i += 1

    print("Done!")


def download_from_json(filename, dest_folder):
    """ Downloads all videos from an existing JSON file. """
    links = video_links_from_file(filename)
    download_all_videos(links, dest_folder)


def video_links_to_file(filename):
    """ Outputs all the lecture titles and direct links to a JSON file. """
    with open(filename, 'w') as json_data:
        json_data.write(json.dumps(video_links, indent=4, sort_keys=True))


def video_links_from_file(filename):
    """ Reads the JSON file that's already been populated. """
    if not pathlib.Path(filename).is_file():
        raise IOError("{} does not exist...".format(filename))
    else:
        with open(filename) as json_data:
            video_links = json.load(json_data)

        return video_links
