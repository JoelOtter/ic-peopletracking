from fabric.api import env
from fabric.operations import run, get, prompt
import getpass
import os

env.hosts = ['guest@cvm-g1436217.doc.ic.ac.uk']
env.port = '55022'

def get_video():
  env.password = getpass.getpass('Password: ')
  run('mkdir -p /home/guest/videos/')
  videos = get('/home/guest/videos/', '%(dirname)s/%(basename)s')
