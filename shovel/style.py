import os
from shovel import task


@task
def pep8():

    '''runs pep8 style check'''

    success = os.system('pep8') == 0
    if not success:
        raise Exception('pep8 style check failed')


@task
def jslint():

    '''runs jslint for javascript styles'''

    success = os.system(
        "find . -name \"*.js\" -print0"
        "  | xargs jslint"
    ) == 0

    if not success:
        print "\n"  # clear for jslint output
        raise Exception('jslint style check failed')

