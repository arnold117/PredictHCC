# coding:utf-8
'''
This tool is to simplify the steps to download TCGA data.The tool has two main parameters,
-m is the manifest file path.
-s is the location where the downloaded file is to be saved (it is best to create a new folder for the downloaded data).
This tool supports breakpoint resuming. After the program is interrupted, it can be restarted,and the program will download file after the last downloaded file.
If necessary, press ctrl+c to terminate the program.
'''
import os
import pandas as pd
import requests
import sys
import argparse
import signal

print(__doc__)

requests.packages.urllib3.disable_warnings()


def download(url, file_path):
    r = requests.get(url, stream=True, verify=False)
    total_size = int(r.headers['content-length'])
    # print(total_size)
    temp_size = 0

    with open(file_path, "wb") as f:

        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('#' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    print()


def get_UUID_list(manifest_path):
    df = pd.read_table(manifest_path, sep='\t', encoding='utf-8')
    UUID_filename_list = list(zip(df['id'], df['filename']))
    return UUID_filename_list


def get_last_UUID(file_path):
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    else:
        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)))

        return dir_list[-1][:-4]


def get_lastUUID_index(UUID_list, last_UUID):
    for i, UUID in enumerate(UUID_list):
        if UUID == last_UUID:
            return i
    return 0


def quit(signum, frame):
    # Ctrl+C quit
    print('You choose to stop me.')
    exit()
    print()


if __name__ == '__main__':

    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--manifest", dest="M", type=str, default="gdc_manifest.txt",
                        help="gdc_manifest.txt file path")
    parser.add_argument("-s", "--save", dest="S", type=str, default=os.curdir,
                        help="Which folder is the download file saved to?")
    args = parser.parse_args()

    link = r'https://api.gdc.cancer.gov/data/'

    # args
    manifest_path = args.M
    save_path = args.S

    print("Save file to {}".format(save_path))

    UUID_list = get_UUID_list(manifest_path)
    last_UUID = get_last_UUID(save_path)
    print("Last download file {}".format(last_UUID))
    last_UUID_index = get_lastUUID_index(UUID_list, last_UUID)

    for UUID, filename in UUID_list[last_UUID_index:]:
        url = os.path.join(link, UUID)
        file_path = os.path.join(save_path, filename)  # Use the original filename
        download(url, file_path)
        print(f'{filename} have been downloaded')