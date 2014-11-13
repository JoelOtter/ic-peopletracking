var FRAMERATE = 25;

var vid = null;
var canvas = null;
var ctx = null;
var gen = null;
var recentFrame = 0;
var allframes = [];
var vidplaying = false;
var rectWidth = 0;
var rectHeight = 0;

var mouseMovedCanvas = function(evt) {
    // Get data
    if (vid.paused) return;
    var rect = canvas.getBoundingClientRect();
    var frame = secondsToFrames(vid.currentTime);
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
    }

    // Draw rectangle
    frameData.rectangles.forEach(function(r) {
        ctx.clearRect(0, 0, canv.width, canv.height);
        ctx.fillStyle='rgba(255, 0, 0, 0.5)';
        ctx.fillRect(r.x, r.y, r.width, r.height);
    });
};

var secondsToFrames = function(seconds) {
    return seconds * FRAMERATE;
};

var playVid = function() {
    if (!vidplaying) {
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

window.onload = function() {
    vid = $('#vid')[0];
    canvas = $('#canv')[0];
    gen = $('#generated')[0];
    var write = $('#write')[0];
    vid.addEventListener('loadeddata', function() {
        $('#canv').css('width', vid.videoWidth);
        $('#canv').css('height', vid.videoHeight);
        $('#canv').prop('width', vid.videoWidth);
        $('#canv').prop('height', vid.videoHeight);
    });
    vid.addEventListener('play', function() {
        vidplaying = true;
    });
    vid.addEventListener('pause', function() {
        vidplaying = false;
        ctx.clearRect(0, 0, canv.width, canv.height);
    });
    canvas.addEventListener('mousemove', mouseMovedCanvas);
    canvas.addEventListener('mouseout', function() {
        ctx.clearRect(0, 0, canv.width, canv.height);
    });
    ctx = canvas.getContext('2d');
    $('body').keypress(function(e) {
        if (e.keyCode == 32) {
            playVid();
        }
    });
    $('#width').trigger('change');
    $('#height').trigger('change');
};
