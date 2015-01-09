/*jslint browser:true */
/*global $, _ */

var FRAMERATE = 25;
var SPACE_KEY = 32;

var RED = 'rgba(255, 0, 0, 0.5)',
    GREEN = 'rgba(0, 255, 0, 0.5)';

var vid, canvas, ctx, gen, frameTimer = null;
var recentFrame = 0;
var allFrames = {},
    currentFrames = {};
var rectWidth, rectHeight, mouseX, mouseY = 0;
var mouseDown, mouseOnCanvas = false;
var rectID = "";

var secondsToFrames = function(seconds) {
    return seconds * FRAMERATE;
};

var clearCanvas = function() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
};

var drawRectAtCoords = function(r, col) {
    ctx.fillStyle = col;
    ctx.fillRect(r.x, r.y, r.width, r.height);
};

var drawRectAtMouse = function(col) {
    var canvR =  canvas.getBoundingClientRect();
    ctx.fillStyle = col;
    ctx.fillRect(mouseX - canvR.left - rectWidth/2,
                 mouseY - canvR.top - rectHeight/2, rectWidth, rectHeight);
};

var captureFrameData = function() {
    if (vid.paused || !mouseDown || !mouseOnCanvas) {
        return;
    }
    var frame = secondsToFrames(vid.currentTime);
    var frameData = {};
    frame = Math.floor(frame);
    if (frame > recentFrame) {
        recentFrame = frame;
        var canvR = canvas.getBoundingClientRect();
        frameData = {
            id: rectID,
            x: mouseX - canvR.left - rectWidth/2,
            y: mouseY - canvR.top - rectHeight/2,
            width: rectWidth,
            height: rectHeight
        };
        currentFrames[frame] = frameData;
        gen.innerHTML = JSON.stringify(currentFrames);
        
        // Draw rectangle
        clearCanvas();
        drawRectAtCoords(frameData, RED);
    }

};

var mouseMovedCanvas = function(evt) {
    mouseOnCanvas = true;
    mouseX = evt.clientX;
    mouseY = evt.clientY;
};

var mouseScrolled = function(e) {
    e.preventDefault();
    var newWidth = rectWidth + e.originalEvent.wheelDelta / 4;
    rectHeight = Math.round(rectHeight * (newWidth / rectWidth));
    rectWidth = Math.round(newWidth);
    $('#width').val(rectWidth);
    $('#height').val(rectHeight);
    clearCanvas();
    var col = mouseDown ? RED : GREEN;
    drawRectAtMouse(col);
};

var playVid = function() {
    if (vid.paused) {
        vid.play();
        recentFrame = 0;
    }
};

var mergeFrames = function() {
    console.log(allFrames);
    var keys = [];
    for (var r in allFrames) {
        keys = _.union(keys, Object.keys(allFrames[r]));
    }
    var res = [];
    for (var k in keys) {
        var rects = [];
        var frameNum = parseInt(k);
        for (var rect in allFrames) {
            if (_.has(allFrames[rect], frameNum)) {
                rects.push(allFrames[rect][frameNum]);
            }
        }
        if (rects.length > 0) {
            res.push({frame: frameNum, rectangles: rects});
        }
    }
    return res;
};

var writeToFile = function(vfolder, vfile) {
    $('#write').prop('disabled', true);
    $.ajax({
        type: 'POST',
        url: '/write',
        data: {
            framedata: JSON.stringify(mergeFrames()),
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

var setRectID = function(val) {
    rectID = val;
};

var clearCanvas = function() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
};

var setupEvents = function() {
    vid.addEventListener('loadeddata', function() {
        $('#canv').css('width', vid.videoWidth);
        $('#canv').css('height', vid.videoHeight);
        $('#canv').prop('width', vid.videoWidth);
        $('#canv').prop('height', vid.videoHeight);
    });
    vid.addEventListener('play', function() {
        frameTimer = setInterval(captureFrameData, 1000/FRAMERATE);
    });
    vid.addEventListener('pause', function() {
        clearInterval(frameTimer);
        clearCanvas();
        allFrames[rectID] = currentFrames;
        currentFrames = {};
    });
    canvas.addEventListener('mousemove', mouseMovedCanvas);
    canvas.addEventListener('mouseout', function() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        mouseOnCanvas = false;
    });
    $('#canv').on('DOMMouseScroll mousewheel', mouseScrolled);
    document.addEventListener('mousedown', function() {
        mouseDown = true;
    });
    document.addEventListener('mouseup', function() {
        clearCanvas();
        mouseDown = false;
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
