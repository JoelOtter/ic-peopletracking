/*jslint browser:true */
/*global $, FileReader */

var FRAMES_PER_SECOND = 25;
var SPACE_KEY = 32;

var video, canvas, ctx, drawTimer = null;
var allframes = [];

var getFrame = function(frameNumber) {
    var frame = Math.floor(frameNumber);
    var result = $.grep(allframes, function(f){ return f.frame === frame; });
    return result[0];
};

var drawOnFrame = function() {
    var frameData = getFrame(video.currentTime * FRAMES_PER_SECOND);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (frameData) {
        frameData.rectangles.forEach(function(r) {
            ctx.fillStyle='rgba(255, 0, 0, 0.5)';
            ctx.fillRect(r.x, r.y, r.width, r.height);
        });
    }
};

var loadJson = function(evt) {
    var f = evt.target.files[0];
    var reader = new FileReader();
    reader.onload = function(e) {
        allframes = JSON.parse(e.target.result);
    };
    reader.readAsText(f, 'UTF-8');
};

var registerEvents = function() {
    $('#vidpicker')[0].addEventListener('change', function(evt) {
        video.src = window.URL.createObjectURL(evt.target.files[0]);
    });
    $('#jsonpicker')[0].addEventListener('change', loadJson);
    video.addEventListener('loadeddata', function() {
        $('#canv').css('width', video.videoWidth);
        $('#canv').css('height', video.videoHeight);
        $('#canv').prop('width', video.videoWidth);
        $('#canv').prop('height', video.videoHeight);
    });
    video.addEventListener('play', function() {
        drawTimer = setInterval(drawOnFrame, 1000/FRAMES_PER_SECOND);
    });
    video.addEventListener('pause', function() {
        clearInterval(drawTimer);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });
    $('body').keypress(function(e) {
        if (e.keyCode === SPACE_KEY) {
            video.play();
        }
    });

};

$(document).ready(function() {
    video = $('#vid')[0];
    canvas = $('#canv')[0];
    ctx = canvas.getContext('2d');
    registerEvents();
});
