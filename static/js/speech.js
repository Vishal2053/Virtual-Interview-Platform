// Speech-related functionality for the interview app

/**
 * Text-to-Speech function using the Web Speech API
 * @param {string} text - The text to convert to speech
 * @param {Object} options - Optional configuration for the speech
 */
function speakText(text, options = {}) {
    return new Promise((resolve, reject) => {
      // Check if browser supports speech synthesis
      if (!('speechSynthesis' in window)) {
        console.error('Text-to-speech not supported in this browser');
        reject(new Error('Text-to-speech not supported'));
        return;
      }
      
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      // Create utterance
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set options
      utterance.rate = options.rate || 1;
      utterance.pitch = options.pitch || 1;
      utterance.volume = options.volume || 1;
      
      // Set voice if specified
      if (options.voice) {
        const voices = window.speechSynthesis.getVoices();
        const selectedVoice = voices.find(v => v.name === options.voice);
        if (selectedVoice) {
          utterance.voice = selectedVoice;
        }
      }
      
      // Event handlers
      utterance.onend = () => resolve();
      utterance.onerror = event => reject(new Error(`Speech synthesis error: ${event.error}`));
      
      // Speak the text
      window.speechSynthesis.speak(utterance);
    });
  }
  
  /**
   * Speech recognition function using the Web Speech API
   * @param {Object} options - Configuration options
   * @returns {Object} - Speech recognition controller
   */
  function createSpeechRecognition(options = {}) {
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.error('Speech recognition not supported in this browser');
      return null;
    }
    
    // Create recognition instance
    const recognition = new SpeechRecognition();
    
    // Set options
    recognition.continuous = options.continuous !== false;
    recognition.interimResults = options.interimResults !== false;
    recognition.lang = options.lang || 'en-US';
    
    // State
    let isListening = false;
    let transcript = '';
    
    // Return controller object
    return {
      /**
       * Start listening
       */
      start() {
        if (isListening) return;
        
        // Reset transcript if not continuous
        if (!options.preserveTranscript) {
          transcript = '';
        }
        
        try {
          recognition.start();
          isListening = true;
        } catch (err) {
          console.error('Error starting speech recognition:', err);
          throw err;
        }
      },
      
      /**
       * Stop listening
       */
      stop() {
        if (!isListening) return;
        
        try {
          recognition.stop();
          isListening = false;
        } catch (err) {
          console.error('Error stopping speech recognition:', err);
        }
      },
      
      /**
       * Get current transcript
       */
      getTranscript() {
        return transcript;
      },
      
      /**
       * Set event handlers
       */
      setHandlers(handlers) {
        if (handlers.onStart) {
          recognition.onstart = () => {
            isListening = true;
            handlers.onStart();
          };
        }
        
        if (handlers.onEnd) {
          recognition.onend = () => {
            isListening = false;
            handlers.onEnd();
          };
        }
        
        if (handlers.onResult) {
          recognition.onresult = (event) => {
            let newTranscript = '';
            let isFinal = false;
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
              newTranscript += event.results[i][0].transcript;
              if (event.results[i].isFinal) {
                isFinal = true;
              }
            }
            
            if (options.preserveTranscript) {
              transcript += ' ' + newTranscript;
              transcript = transcript.trim();
            } else {
              transcript = newTranscript;
            }
            
            handlers.onResult({
              transcript,
              isFinal
            });
          };
        }
        
        if (handlers.onError) {
          recognition.onerror = (event) => {
            handlers.onError(event);
          };
        }
      },
      
      /**
       * Check if currently listening
       */
      isListening() {
        return isListening;
      }
    };
  }