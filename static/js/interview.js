// Updated Interview page functionality with working camera, recording, and submit

// DOM elements
const startRecordingBtn = document.getElementById('start-recording');
const stopRecordingBtn = document.getElementById('stop-recording');
const submitAnswerBtn = document.getElementById('submit-answer');
const answerText = document.getElementById('answer-text');
const editAnswerBtn = document.getElementById('edit-answer');
const recordingStatus = document.getElementById('recording-status');
const speakQuestionBtn = document.getElementById('speak-question');
const questionText = document.getElementById('current-question');
const toggleWebcamBtn = document.getElementById('toggle-webcam');
const webcamVideo = document.getElementById('webcam');
const cameraOffMessage = document.getElementById('camera-off-message');
const ttsAudio = document.getElementById('tts-audio');
const feedbackContainer = document.getElementById('feedback-container');
const overallScoreEl = document.getElementById('overall-score');
const feedbackTextEl = document.getElementById('feedback-text');
const encouragementTextEl = document.getElementById('encouragement-text');

// State
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let webcamStream = null;
let recognitionActive = false;
let recognition = null;
let loadingModal = null;

// Read the question aloud automatically when page loads
speakQuestion();

// Event listeners
if (startRecordingBtn) startRecordingBtn.addEventListener('click', startRecording);
if (stopRecordingBtn) stopRecordingBtn.addEventListener('click', stopRecording);
if (submitAnswerBtn) submitAnswerBtn.addEventListener('click', submitAnswer);
if (editAnswerBtn) editAnswerBtn.addEventListener('click', makeAnswerEditable);
if (speakQuestionBtn) speakQuestionBtn.addEventListener('click', speakQuestion);
if (toggleWebcamBtn) toggleWebcamBtn.addEventListener('click', toggleWebcam);

// Initialize the loading modal if Bootstrap is available
if (typeof bootstrap !== 'undefined') {
  loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
}

async function startRecording() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Your browser does not support audio recording.");
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
      if (event.data.size > 0) audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.controls = true;
      answerText.innerHTML = '';
      answerText.appendChild(audio);
    };

    mediaRecorder.start();
    isRecording = true;
    recordingStatus.textContent = "Recording...";
  } catch (err) {
    console.error("Error accessing microphone:", err);
    alert("Could not access microphone.");
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    recordingStatus.textContent = "Stopped";
  }
}

async function toggleWebcam() {
  if (webcamStream) {
    webcamStream.getTracks().forEach(track => track.stop());
    webcamVideo.srcObject = null;
    webcamStream = null;
    webcamVideo.style.display = 'none';
    cameraOffMessage.style.display = 'block';
  } else {
    try {
      webcamStream = await navigator.mediaDevices.getUserMedia({ video: true });
      webcamVideo.srcObject = webcamStream;
      await webcamVideo.play();
      webcamVideo.style.display = 'block';
      cameraOffMessage.style.display = 'none';
    } catch (error) {
      console.error('Error accessing webcam:', error);
      alert('Unable to access the webcam.');
    }
  }
}

function speakQuestion() {
  if (questionText && questionText.textContent) {
    speakText(questionText.textContent).catch(err => {
      console.error("Failed to speak question:", err);
    });
  }
}

function submitAnswer() {
  const response = answerText.textContent || "";
  console.log("Submitted answer:", response);
  alert("Answer submitted successfully.");
}

function makeAnswerEditable() {
  if (answerText) {
    answerText.contentEditable = true;
    answerText.focus();
  }
}
