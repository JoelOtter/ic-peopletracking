#!/usr/bin/env python

import os
from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/create/<vfolder>/<vfile>')
def test_creator(vfolder, vfile):
    if not os.path.exists('static/' + vfolder + vfile + '.mp4'):
        os.symlink('../../tests/videos/' + vfolder + '/' + vfile + '.mp4',
                   'static/' + vfolder + vfile + '.mp4')
    return render_template('testcreator.html', vfolder=vfolder, vfile=vfile)


@app.route('/view')
def test_viewer():
    return render_template('viewer.html')


@app.route('/write', methods=['POST'])
def write_to_file():
    rf = request.form
    outputFile = open('../tests/videos/' + rf['vfolder']
                      + '/' + rf['vfile'] + '.json', 'w')
    outputFile.write(rf['framedata'])
    return 'OK, written to file'

if __name__ == '__main__':
    app.run(debug=True)
