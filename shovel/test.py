import os
import re
import sys
import json
from subprocess import call, check_output
from shovel import task
from track import test, Tracker

VM_CONF = {
    'host': 'cvm-g1436217.doc.ic.ac.uk',
    'user': 'guest',
    'port': 55022,
    'videoPath': '/home/guest/videos/'
}

videoPath = os.path.join(os.getcwd(), 'tests/videos')

TEST_CONF = {
    'videoPath': videoPath,
    'escapedVideoPath': videoPath.replace(' ', r'\ ')
}

TICK = u'\u2714'
CROSS = u'\u2717'
ENDC = '\033[0m'
RED = '\033[1;31m'
GREEN = '\033[1;32m'


@task
def fetch_videos():

    '''fetches videos from the VM host'''

    rsyncVersion = re.match('.*version\s+([^\s]+)', check_output(['rsync', '--version'])).group(1)
    if rsyncVersion < '3.0.0':
        raise Exception('Rsync version must be greater than 3.0.0')

    call(
        (
            "rsync -avz -e \"ssh -p {port}\" "
            "--exclude \"*.json\" "
            "{user}@{host}:{videoPath} {localPath}"
        ).format(localPath=TEST_CONF['escapedVideoPath'], **VM_CONF),
        shell=True
    )


@task
def clean():

    '''removes all videos from test directory'''

    ignorePatterns = open(os.path.join(TEST_CONF['videoPath'], '.gitignore')).read().splitlines()
    junkExtensions = filter(lambda ignore: bool(re.match('\*\.[^\.]+$', ignore)), ignorePatterns)
    findCriteria = ' -o '.join('-name "{ext}"'.format(ext=ext) for ext in junkExtensions)

    print 'Removing all test files matching:', junkExtensions

    findCommand = (
        "find {escapedVideoPath} \( {findCriteria} \) -type f "
    ).format(findCriteria=findCriteria, **TEST_CONF) + '-exec rm -vf {} \;'

    print os.system(findCommand)


@task
def all_overlaps():
    '''runs overlap test on all JSON test data'''
    test_files = []
    fails = 0
    for root, dirs, files in os.walk(TEST_CONF['videoPath']):
        for f in files:
            if f.endswith('.json'):
                test_files.append(os.path.join(root, f))

    for f in test_files:
        video_file = f[:-4] + 'mp4'
        expected_data = json.load(open(f, 'r'))
        actual_data = Tracker(video_file, 853, 480).analyse()
        overlap_pcts = test.generate_frame_overlaps(actual_data, expected_data)
        avg = round((sum(overlap_pcts) / len(overlap_pcts)), 1)
        name = '/'.join(f[:-5].split('/')[-2:])
        if (avg < 50):
            fails += 1
            linestart = RED + CROSS
        else:
            linestart = GREEN + TICK
        print linestart + ' ' + str(avg) + '%' + ' ' + name + ENDC

    sys.exit(fails)
