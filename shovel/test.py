import os
import re
from subprocess import call, check_output
from shovel import task

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

    escapedVideoPath = TEST_CONF['videoPath'].replace(' ', '\ ')

    ignorePatterns = open(os.path.join(TEST_CONF['videoPath'], '.gitignore')).read().splitlines()
    junkExtensions = filter(lambda ignore: bool(re.match('\*\.[^\.]+$', ignore)), ignorePatterns)
    findCriteria = ' -o '.join('-name "{ext}"'.format(ext=ext) for ext in junkExtensions)

    print 'Removing all test files matching:', junkExtensions

    findCommand = (
        "find {escapedVideoPath} \( {findCriteria} \) -type f "
    ).format(findCriteria=findCriteria, **TEST_CONF) + '-exec rm -vf {} \;'

    print os.system(findCommand)

