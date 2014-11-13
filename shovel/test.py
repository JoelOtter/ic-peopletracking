import os
from subprocess import call
from shovel import task

VM_CONF = {
    'host': 'cvm-g1436217.doc.ic.ac.uk',
    'user': 'guest',
    'port': 55022,
    'pass': os.environ['PEOPLE_TRACKER_VM_PASSWORD'],
    'videoPath': '/home/guest/videos'
}

TEST_CONF = {
    'videoPath': os.path.join(os.getcwd(), 'tests/videos')
}


@task
def fetch_videos():

    '''fetches videos from the VM host'''

    call(
        (
            "rsync -avz -e \"ssh -p {port}\" "
            "--exclude \"*.json\" "
            "{user}@{host}:{videoPath} {localPath}"
        ).format(localPath=TEST_CONF['videoPath'], **VM_CONF),
        shell=True
    )


@task
def clean():

    '''removes all videos from test directory'''

    junkExtensions = open(os.path.join(TEST_CONF['videoPath'], '.gitignore')).read().splitlines()
    findCriteria = ' -o '.join('-name "{ext}"'.format(ext=ext) for ext in junkExtensions)

    print 'Removing all test files matching:', junkExtensions

    findCommand = (
        "find {videoPath} \( {findCriteria} \) -type f "
    ).format(findCriteria=findCriteria, **TEST_CONF) + '-exec rm -vf {} \;'

    call(findCommand, shell=True)

