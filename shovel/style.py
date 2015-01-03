import os
import fnmatch
from shovel import task


# Finds all files that match the wildcard pattern or have a name equal to a pattern.
def find_files(pattern):
    matched_files = []
    for root, dirnames, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            if (filename == pattern) or fnmatch.fnmatch(filename, pattern):
                matched_files.append(os.path.join(root, filename))
    return matched_files


# Generates a lambda that can be queried with a filepath to verify if that file is
# ignored by git.
def get_ignore_rules():
    ignore_patterns = []
    for gitignore in find_files('.gitignore'):
        ignore_patterns.extend([
            os.path.join(os.path.dirname(gitignore), line.rstrip()) for line in open(gitignore)
        ])
    is_ignored = lambda filepath, ptn: (ptn in filepath) or fnmatch.fnmatch(filepath, ptn)
    return lambda filepath: True in [is_ignored(filepath, p) for p in ignore_patterns]


@task
def all_none_ignored_js():

    is_ignored = get_ignore_rules()
    return [filepath for filepath in find_files('*.js') if not is_ignored(filepath)]


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
        "jslint " + ' '.join(all_none_ignored_js())
    ) == 0

    if not success:
        print "\n"  # clear for jslint output
        raise Exception('jslint style check failed')

