from setuptools import setup

setup(
    name='ic-peopletracking',
    version='0.1',
    description='Tracking humans from a camera feed or video file.',
    url='https://github.com/JoelOtter/ic-peopletracking',
    author='IC Group 17',
    scripts=['bin/vidtojson', 'bin/cameratojson'],
    install_requires=['numpy==1.9.0']
)
