/*jslint browser:true */
/*global $ */

var FRAMERATE = 25;
var SPACE_KEY = 32;

var RED = 'rgba(255, 0, 0, 0.5)',
    GREEN = 'rgba(0, 255, 0, 0.5)';

var vid, canvas, ctx, gen, frameTimer = null;
var recentFrame = 0;
var allframes = [];
var rectWidth, rectHeight, mouseX, mouseY = 0;
var mouseDown, mouseOnCanvas = false;

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
    console.log('capture');
    var frame = secondsToFrames(vid.currentTime);
    var frameData = {};
    frame = Math.floor(frame);
    if (frame > recentFrame) {
        recentFrame = frame;
        var canvR = canvas.getBoundingClientRect();
        frameData = {
            frame: frame,
            rectangles: [
            {
                id: '',
                x: mouseX - canvR.left - rectWidth/2,
                y: mouseY - canvR.top - rectHeight/2,
                width: rectWidth,
                height: rectHeight
            }
            ]
        };
        allframes.push(frameData);
        gen.innerHTML = JSON.stringify(allframes);
        
        // Draw rectangle
        clearCanvas();
        frameData.rectangles.forEach(function(r) {
            drawRectAtCoords(r, RED);
        });
    }

};

var mouseMovedCanvas = function(evt) {
    mouseOnCanvas = true;
    mouseX = evt.clientX;
    mouseY = evt.clientY;
};

var mouseScrolled = function(e) {
    e.preventDefault();
    var newWidth = rectWidth + e.originalEvent.wheelDelta;
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
