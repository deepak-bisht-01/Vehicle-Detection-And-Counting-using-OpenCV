let videoElement = document.getElementById('videoFeed');
let captureBtn = document.getElementById('captureBtn');
let startBtn = document.getElementById('startCamera');
let canvas = document.getElementById('photoCanvas');
let ctx = canvas.getContext('2d');
let photoData = document.getElementById('photoData');
let userInput = document.getElementById('userInput');

startBtn.addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            videoElement.srcObject = stream;
            videoElement.play();
            startBtn.classList.add('hidden');
            captureBtn.classList.remove('hidden');
        })
        .catch(function(err) {
            alert('Camera access required');
        });
});

captureBtn.addEventListener('click', function() {
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    ctx.drawImage(videoElement, 0, 0);
    photoData.value = canvas.toDataURL('image/jpeg');
    alert('Photo captured!');
});

document.getElementById('mainForm').addEventListener('submit', function(e) {
    e.preventDefault();
    if (!userInput.value) {
        alert('Please enter text');
        return;
    }
    if (!photoData.value) {
        alert('Please capture photo');
        return;
    }
    
    let formData = {
        text: userInput.value,
        image: photoData.value
    };
    
    console.log('Submission:', formData);
    alert('Data captured successfully');
    this.reset();
    photoData.value = '';
});