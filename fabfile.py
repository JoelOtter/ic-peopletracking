from fabric.operations import run, get, local

remotePath = '/home/guest/videos/'
localPath   = 'tests/videos'


def get_videos():
    local('rsync -avz -e "ssh -p 55022" --exclude "*.json" guest@cvm-g1436217.doc.ic.ac.uk:' 
                                                             + remotePath + ' ' + localPath)


def remove_videos():
    local('cd tests')
    local('find . -name "*.avi" -type f -delete')
    local('find . -name "*.mp4" -type f -delete')
