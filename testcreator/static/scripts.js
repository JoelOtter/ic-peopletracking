var FRAMERATE = 25;

var vid = null;
var canvas = null;
var gen = null;
var recentFrame = 0;
var allframes = [];

var mouseMovedCanvas = function(evt) {
    if (vid.ended) return;
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
                x: evt.clientX - rect.left,
                y: evt.clientY - rect.top
            }
            ]
        };
        allframes.push(frameData);
        gen.innerHTML = JSON.stringify(allframes);
    }
};

var secondsToFrames = function(seconds) {
    return seconds * FRAMERATE;
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
            console.log("hello");
            $('#write').html('Success!');
        }
    });
};

window.onload = function() {
    vid = $("#vid")[0];
    canvas = $("#canv")[0];
    gen = $("#generated")[0];
    var write = $("#write")[0];
    vid.addEventListener('loadeddata', function() {
        $("#canv").css("width", vid.videoWidth);
        $("#canv").css("height", vid.videoHeight);
        vid.play();
    });
    canvas.addEventListener("mousemove", mouseMovedCanvas);
};
