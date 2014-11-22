/*jslint browser:true */
/*global $ */

var FRAMERATE = 25;
var SPACE_KEY = 32;

var vid, canvas, ctx, gen = null;
var recentFrame = 0;
var allframes = [];
var rectWidth = 0;
var rectHeight = 0;
var mouseDown = false;

var secondsToFrames = function(seconds) {
    return seconds * FRAMERATE;
};

var mouseMovedCanvas = function(evt) {
    // Get data
    if (vid.paused || !mouseDown) {
        return;
    }
    var rect = canvas.getBoundingClientRect();
    var frame = secondsToFrames(vid.currentTime);
    var frameData = {};
    frame = Math.floor(frame);
    if (frame > recentFrame) {
        recentFrame = frame;
        frameData = {
            frame: frame,
            rectangles: [
            {
                id: '',
                x: evt.clientX - rect.left - rectWidth/2,
                y: evt.clientY - rect.top - rectHeight/2,
                width: rectWidth,
                height: rectHeight
            }
            ]
        };
        allframes.push(frameData);
        gen.innerHTML = JSON.stringify(allframes);
        
        // Draw rectangle
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        frameData.rectangles.forEach(function(r) {
            ctx.fillStyle='rgba(255, 0, 0, 0.5)';
            ctx.fillRect(r.x, r.y, r.width, r.height);
        });
    }
};

var playVid = function() {
    if (vid.paused) {
        vid.play();
        allframes = [];
        recentFrame = 0;
        gen.innerHTML = JSON.stringify(allframes);
    }
};

var writeToFile = function(vfolder, vfile) {
    $('#write').prop('disabled', true);
    $.ajax({
        type: 'POST',
        url: '/write',
        data: {
            framedata: JSON.stringify(allframes),
            vfolder: vfolder,
            vfile: vfile
        },
        success: function() {
            $('#write').html('Success!');
        }
    });
};

var setRectWidth = function(val) {
    rectWidth = parseFloat(val);
};
var setRectHeight = function(val) {
    rectHeight = parseFloat(val);
};

var clearCanvas = function() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    mouseDown = false;
};

var setupEvents = function() {
    vid.addEventListener('loadeddata', function() {
        $('#canv').css('width', vid.videoWidth);
        $('#canv').css('height', vid.videoHeight);
        $('#canv').prop('width', vid.videoWidth);
        $('#canv').prop('height', vid.videoHeight);
    });
    vid.addEventListener('pause', function() {
        clearCanvas();
    });
    canvas.addEventListener('mousemove', mouseMovedCanvas);
    canvas.addEventListener('mouseout', function() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });
    canvas.addEventListener('mousedown', function() {
        mouseDown = true;
    });
    canvas.addEventListener('mouseup', function() {
        clearCanvas();
    });
    $('body').keypress(function(e) {
        if (e.keyCode === SPACE_KEY) {
            playVid();
        }
    });
};

$(document).ready(function() {
    vid = $('#vid')[0];
    canvas = $('#canv')[0];
    gen = $('#generated')[0];
    ctx = canvas.getContext('2d');
    setupEvents();
    $('#width').trigger('change');
    $('#height').trigger('change');
});
