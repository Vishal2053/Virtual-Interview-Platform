// Speech-related functionality for the interview app

/**
 * Text-to-Speech function using the Web Speech API
 * @param {string} text - The text to convert to speech
 * @param {Object} options - Optional configuration for the speech
 */
function speakText(text, options = {}) {
    return new Promise((resolve, reject) => {
      if (!('speechSynthesis' in window)) {
        console.error('Text-to-speech not supported in this browser');
        reject(new Error('Text-to-speech not supported'));
        return;
      }
      
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      utterance.rate = options.rate || 1;
      utterance.pitch = options.pitch || 1;
      utterance.volume = options.volume || 1;
      
      if (options.voice) {
        const voices = window.speechSynthesis.getVoices();
        const selectedVoice = voices.find(v => v.name === options.voice);
        if (selectedVoice) {
          utterance.voice = selectedVoice;
        }
      }
      
      utterance.onend = () => resolve();
      utterance.onerror = event => reject(new Error(`Speech synthesis error: ${event.error}`));
      
      window.speechSynthesis.speak(utterance);
    });
}