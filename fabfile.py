from fabric.operations import local

remotePath = '/home/guest/videos/'
localPath = 'tests/videos'


def fetch():
    local('rsync -avz -e "ssh -p 55022" --exclude "*.json" guest@cvm-g1436217.doc.ic.ac.uk:'
          + remotePath + ' ' + localPath)


def clean():
    local('find tests/videos/ \( -name "*.avi" -o -name "*.mp4" \) -type f -delete')
