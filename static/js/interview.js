// interview.js - FINAL FIXED VERSION

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

let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let stream = null;
let webcamStream = null;
let loadingModal = null;
let audioBlob = null;
let transcript = '';

speakQuestion();

if (startRecordingBtn) startRecordingBtn.addEventListener('click', startRecording);
if (stopRecordingBtn) stopRecordingBtn.addEventListener('click', stopRecording);
if (submitAnswerBtn) submitAnswerBtn.addEventListener('click', submitAnswer);
if (editAnswerBtn) editAnswerBtn.addEventListener('click', makeAnswerEditable);
if (speakQuestionBtn) speakQuestionBtn.addEventListener('click', speakQuestion);
if (toggleWebcamBtn) toggleWebcamBtn.addEventListener('click', toggleWebcam);

if (typeof bootstrap !== 'undefined') {
  loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'), {
    backdrop: 'static',
    keyboard: false
  });
}

async function startRecording() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    transcript = '';
    answerText.value = 'Recording...';

    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {
      audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      try {
        loadingModal?.show();
        const res = await fetch('/transcribe', { method: 'POST', body: formData });
        const result = await res.json();
        transcript = result.transcript || 'No transcription available. Please edit or retry.';
      } catch (err) {
        showError(`Transcription failed: ${err.message}`);
        transcript = 'Transcription failed. Please type your answer.';
      } finally {
        loadingModal?.hide();
      }

      answerText.value = transcript;
      recordingStatus.textContent = "Stopped";
      isRecording = false;
      stream.getTracks().forEach(track => track.stop());
      mediaRecorder = null;
      startRecordingBtn.disabled = false;
      stopRecordingBtn.disabled = true;
      submitAnswerBtn.disabled = false;
    };

    mediaRecorder.start();
    isRecording = true;
    recordingStatus.textContent = "Recording...";
    startRecordingBtn.disabled = true;
    stopRecordingBtn.disabled = false;
    submitAnswerBtn.disabled = true;
  } catch (err) {
    console.error("Microphone error:", err);
    showError("Microphone access denied.");
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    recordingStatus.textContent = "Stopping...";
    stopRecordingBtn.disabled = true;
  }
}

function makeAnswerEditable() {
  answerText.removeAttribute('readonly');
  answerText.focus();
  answerText.addEventListener('input', () => {
    transcript = answerText.value;
  });
}

async function submitAnswer() {
  const finalAnswer = answerText.value || transcript;
  if (!finalAnswer.trim() || finalAnswer.includes('Transcription failed')) {
    showError("Please record or type your answer.");
    return;
  }

  try {
    loadingModal?.show();

    const response = await fetch('/submit-answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer: finalAnswer })
    });

    const result = await response.json();
    loadingModal?.hide();

    if (result.error) {
      showError(`Submission failed: ${result.error}`);
      return;
    }

    overallScoreEl.textContent = `${result.evaluation.overall_score * 10}%`;
    feedbackTextEl.textContent = result.evaluation.feedback;
    encouragementTextEl.textContent = result.evaluation.encouragement;
    feedbackContainer.style.display = 'block';

    // 🔁 Automatically redirect to next question after short delay
    setTimeout(() => {
      if (result.is_complete) {
        window.location.href = '/results';
      } else {
        window.location.href = `/interview?t=${Date.now()}`;
      }
    }, 2000); // Wait 2s to show feedback

  } catch (err) {
    loadingModal?.hide();
    showError(`Failed to submit answer: ${err.message}`);
  }
}

function toggleWebcam() {
  if (webcamStream) {
    webcamStream.getTracks().forEach(track => track.stop());
    webcamVideo.srcObject = null;
    webcamStream = null;
    webcamVideo.style.display = 'none';
    cameraOffMessage.style.display = 'block';
  } else {
    navigator.mediaDevices.getUserMedia({ video: true }).then(s => {
      webcamStream = s;
      webcamVideo.srcObject = s;
      webcamVideo.play();
      webcamVideo.style.display = 'block';
      cameraOffMessage.style.display = 'none';
    }).catch(err => {
      showError("Unable to access webcam. Check permissions.");
    });
  }
}

function speakQuestion() {
  if (questionText?.textContent) {
    speakText(questionText.textContent).catch(() => {
      fetch('/get-speech').then(res => res.json()).then(data => {
        if (data.audio) {
          ttsAudio.src = `data:audio/mpeg;base64,${data.audio}`;
          ttsAudio.play();
        }
      });
    });
  }
}
