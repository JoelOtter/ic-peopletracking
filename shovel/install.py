import os
from shovel import task


@task
def git_hooks():

    '''symlinks git hooks'''

    print 'Symlinking git hooks .git/hooks -> ../hooks'
    fail = os.system('rm -rf ./.git/hooks && ln -s ../hooks .git/hooks')

    if not fail:
        print 'Installed git hooks!'

    else:
        raise 'Failed to install git hooks'

