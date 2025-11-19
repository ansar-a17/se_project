import axios from 'axios';

// API endpoints
const ORCHESTRATOR_URL = '/api/process';
const TEXT_PROCESS_URL = '/api/process_text';
const HEALTH_URL = '/api/health';

// UI elements
const captureBtn = document.getElementById('captureBtn') as HTMLButtonElement;
const submitTextBtn = document.getElementById('submitTextBtn') as HTMLButtonElement;
const textInput = document.getElementById('textInput') as HTMLTextAreaElement;
const imageModeBtn = document.getElementById('imageModeBtn') as HTMLButtonElement;
const textModeBtn = document.getElementById('textModeBtn') as HTMLButtonElement;
const imageMode = document.getElementById('imageMode') as HTMLDivElement;
const textMode = document.getElementById('textMode') as HTMLDivElement;
const statusSection = document.getElementById('statusSection') as HTMLDivElement;
const translateCheckbox = document.getElementById('translateCheckbox') as HTMLInputElement;
const processingSection = document.getElementById('processingSection') as HTMLDivElement;
const resultsSection = document.getElementById('resultsSection') as HTMLDivElement;
const errorMessage = document.getElementById('errorMessage') as HTMLDivElement;
const previewSection = document.getElementById('previewSection') as HTMLDivElement;
const previewImage = document.getElementById('previewImage') as HTMLImageElement;
const captionText = document.getElementById('captionText') as HTMLDivElement;
const originalText = document.getElementById('originalText') as HTMLDivElement;
const translationBox = document.getElementById('translationBox') as HTMLDivElement;
const audioPlayer = document.getElementById('audioPlayer') as HTMLAudioElement;

// Step UI containers and labels
const step1Container = document.getElementById('step1Container') as HTMLDivElement;
const step2Container = document.getElementById('step2Container') as HTMLDivElement;
const step3Container = document.getElementById('step3Container') as HTMLDivElement;
const step4Container = document.getElementById('step4Container') as HTMLDivElement;
const step1Text = document.getElementById('step1Text') as HTMLDivElement;
const step2Text = document.getElementById('step2Text') as HTMLDivElement;

// Step icons
const step1Icon = document.getElementById('step1Icon') as HTMLDivElement;
const step2Icon = document.getElementById('step2Icon') as HTMLDivElement;
const step3Icon = document.getElementById('step3Icon') as HTMLDivElement;
const step4Icon = document.getElementById('step4Icon') as HTMLDivElement;

let currentMode: 'image' | 'text' = 'image';

// tracking step status
interface ProcessingStep {
  icon: HTMLDivElement;
  status: 'pending' | 'processing' | 'complete' | 'error';
}

// List of steps for UI updates
const steps: ProcessingStep[] = [
  { icon: step1Icon, status: 'pending' },
  { icon: step2Icon, status: 'pending' },
  { icon: step3Icon, status: 'pending' },
  { icon: step4Icon, status: 'pending' }
];

// Update step visibility based on translation toggle and mode
function updateStepVisibility() {
  const isTranslating = translateCheckbox.checked;
  
  if (currentMode === 'image') {
    step1Container.style.display = 'flex';
    step2Container.style.display = 'flex';
    step1Text.textContent = 'Capturing screenshot...';
    step2Text.textContent = 'Analyzing image...';
  } else {
    step1Container.style.display = 'none';
    step2Container.style.display = 'none';
  }
  
  step3Container.style.display = isTranslating ? 'flex' : 'none';
  step4Container.style.display = 'flex';
}

function switchMode(mode: 'image' | 'text') {
  currentMode = mode;
  
  // Update button states
  if (mode === 'image') {
    imageModeBtn.classList.add('active');
    textModeBtn.classList.remove('active');
    imageMode.style.display = 'block';
    textMode.style.display = 'none';
    statusSection.style.display = 'block';
  } else {
    textModeBtn.classList.add('active');
    imageModeBtn.classList.remove('active');
    textMode.style.display = 'block';
    imageMode.style.display = 'none';
    statusSection.style.display = 'none';
  }
  
  hideResults();
  updateStepVisibility();
}

// Update icon appearance and label
function updateStepStatus(stepIndex: number, status: 'pending' | 'processing' | 'complete' | 'error') {
  const step = steps[stepIndex];
  step.status = status;
  
  step.icon.className = `step-icon ${status}`;
  
  if (status === 'complete') {
    step.icon.textContent = 'OK';;
  } else if (status === 'error') {
    step.icon.textContent = 'X';
  } else {
    step.icon.textContent = (stepIndex + 1).toString();
  }
}

// Reset all step icons to pending
function resetSteps() {
  steps.forEach((_, index) => updateStepStatus(index, 'pending'));
  updateStepVisibility();
}

// Display a temporary error message
function showError(message: string) {
  errorMessage.textContent = message;
  errorMessage.classList.add('show');
  setTimeout(() => {
    errorMessage.classList.remove('show');
  }, 5000);
}

// Hide all result-related sections
function hideResults() {
  resultsSection.classList.remove('show');
  previewSection.classList.remove('show');
  processingSection.classList.remove('show');
}

// Capture a screenshot from screen share
async function captureScreenshot(): Promise<Blob> {
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: true,
      audio: false
    });

    const video = document.createElement('video');
    video.srcObject = stream;
    video.play();

    await new Promise(resolve => {
      video.onloadedmetadata = resolve;
    });

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Could not get canvas context');
    
    ctx.drawImage(video, 0, 0);
    
    stream.getTracks().forEach(track => track.stop());

    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Failed to create blob from canvas'));
        }
      }, 'image/png');
    });
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'NotAllowedError') {
        throw new Error('Screen capture permission denied');
      }
      throw error;
    }
    throw new Error('Unknown error during screenshot capture');
  }
}

// Send screenshot to backend orchestrator
async function sendToOrchestrator(imageBlob: Blob, translate: boolean): Promise<{ audio: Blob; caption: string; originalCaption?: string }> {
  const formData = new FormData();
  formData.append('file', imageBlob, 'screenshot.png');

  const url = translate ? `${ORCHESTRATOR_URL}?translate=true` : ORCHESTRATOR_URL;

  const response = await axios.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    responseType: 'blob',
    timeout: 120000
  });

  const caption = response.headers['x-caption-text'] || 'No caption available';
  const originalCaption = response.headers['x-original-text'];
  const wasTranslated = response.headers['x-translated'] === 'true';
  
  return {
    audio: response.data,
    caption: caption,
    originalCaption: wasTranslated ? originalCaption : undefined
  };
}

// Send raw text to backend orchestrator
async function sendTextToOrchestrator(text: string, translate: boolean): Promise<{ audio: Blob; caption: string; originalCaption?: string }> {
  const url = translate ? `${TEXT_PROCESS_URL}?translate=true` : TEXT_PROCESS_URL;

  const response = await axios.post(url, { text }, {
    headers: {
      'Content-Type': 'application/json'
    },
    responseType: 'blob',
    timeout: 120000
  });

  const caption = response.headers['x-caption-text'] || text;
  const originalCaption = response.headers['x-original-text'];
  const wasTranslated = response.headers['x-translated'] === 'true';
  
  return {
    audio: response.data,
    caption: caption,
    originalCaption: wasTranslated ? originalCaption : undefined
  };
}

// Process entered text and update UI
async function processText() {
  const text = textInput.value.trim();
  
  if (!text) {
    showError('Please enter some text to process.');
    return;
  }
  
  submitTextBtn.disabled = true;
  hideResults();
  resetSteps();
  processingSection.classList.add('show');
  previewSection.classList.remove('show');

  const isTranslating = translateCheckbox.checked;

  try {
    const translationStep = 0;
    const finalStep = isTranslating ? 1 : 0;
    
    if (isTranslating) {
      updateStepStatus(translationStep, 'processing');
    }
    
    updateStepStatus(finalStep, 'processing');
    
    const result = await sendTextToOrchestrator(text, isTranslating);
    
    if (isTranslating) {
      updateStepStatus(translationStep, 'complete');
    }
    
    updateStepStatus(finalStep, 'complete');

    // Display results
    captionText.textContent = result.caption;
    
    if (result.originalCaption) {
      originalText.textContent = result.originalCaption;
      translationBox.style.display = 'block';
    } else {
      translationBox.style.display = 'none';
    }
    
    const audioUrl = URL.createObjectURL(result.audio);
    audioPlayer.src = audioUrl;
    
    processingSection.classList.remove('show');
    resultsSection.classList.add('show');
    
    audioPlayer.play();

  } catch (error) {
    console.error('Error processing text:', error);
    
    const currentStep = steps.findIndex(s => s.status === 'processing');
    if (currentStep !== -1) {
      updateStepStatus(currentStep, 'error');
    }

    let errorMsg = 'An error occurred while processing the text.';
    
    if (axios.isAxiosError(error)) {
      const axiosErr = error as any;
      if (axiosErr.code === 'ECONNABORTED') {
        errorMsg = 'Request timed out. Please try again.';
      } else if (axiosErr.response) {
        const status = axiosErr.response.status;
        if (status === 504) {
          errorMsg = 'Request timed out. The AI models may be loading or processing.';
        } else {
          errorMsg = `Server error: ${status}`;
        }
      } else if (axiosErr.request) {
        errorMsg = 'Cannot connect to the server. Make sure the backend services are running.';
      }
    } else if (error instanceof Error) {
      errorMsg = error.message;
    }

    showError(errorMsg);
  } finally {
    submitTextBtn.disabled = false;
  }
}

// Process screenshot and update UI
async function processScreenshot() {
  captureBtn.disabled = true;
  hideResults();
  resetSteps();
  processingSection.classList.add('show');

  const isTranslating = translateCheckbox.checked;

  try {
    updateStepStatus(0, 'processing');
    const imageBlob = await captureScreenshot();
    updateStepStatus(0, 'complete');

    const imageUrl = URL.createObjectURL(imageBlob);
    previewImage.src = imageUrl;
    previewSection.classList.add('show');

    updateStepStatus(1, 'processing');
    
    if (isTranslating) {
      updateStepStatus(2, 'processing');
    }
    
    const finalStepIndex = isTranslating ? 3 : 2;
    updateStepStatus(finalStepIndex, 'processing');
    
    const result = await sendToOrchestrator(imageBlob, isTranslating);
    
    updateStepStatus(1, 'complete');
    
    if (isTranslating) {
      updateStepStatus(2, 'complete');
    }
    
    updateStepStatus(finalStepIndex, 'complete');

    // Display results
    captionText.textContent = result.caption;
    
    if (result.originalCaption) {
      originalText.textContent = result.originalCaption;
      translationBox.style.display = 'block';
    } else {
      translationBox.style.display = 'none';
    }
    
    const audioUrl = URL.createObjectURL(result.audio);
    audioPlayer.src = audioUrl;
    
    processingSection.classList.remove('show');
    resultsSection.classList.add('show');
    
    audioPlayer.play();

  } catch (error) {
    console.error('Error processing screenshot:', error);
    
    const currentStep = steps.findIndex(s => s.status === 'processing');
    if (currentStep !== -1) {
      updateStepStatus(currentStep, 'error');
    }

    let errorMsg = 'An error occurred while processing the screenshot.';
    
    if (axios.isAxiosError(error)) {
      const axiosErr = error as any;
      if (axiosErr.code === 'ECONNABORTED') {
        errorMsg = 'Request timed out. Please try again.';
      } else if (axiosErr.response) {
        const status = axiosErr.response.status;
        if (status === 504) {
          errorMsg = 'Request timed out. The AI models may be loading or processing.';
        } else if (status === 422) {
          errorMsg = 'Image analysis returned empty text. Please try another screenshot.';
        } else {
          errorMsg = `Server error: ${status}`;
        }
      } else if (axiosErr.request) {
        errorMsg = 'Cannot connect to the server. Make sure the backend services are running.';
      }
    } else if (error instanceof Error) {
      errorMsg = error.message;
    }

    showError(errorMsg);
  } finally {
    captureBtn.disabled = false;
  }
}

// Button listeners
captureBtn.addEventListener('click', processScreenshot);
submitTextBtn.addEventListener('click', processText);

// Mode switching
imageModeBtn.addEventListener('click', () => switchMode('image'));
textModeBtn.addEventListener('click', () => switchMode('text'));

// Update step visibility when checkbox changes
translateCheckbox.addEventListener('change', updateStepVisibility);

// Initialize step visibility
updateStepVisibility();

// F9 keyboard shortcut
document.addEventListener('keydown', (event) => {
  if (event.key === 'F9' && !captureBtn.disabled && currentMode === 'image') {
    event.preventDefault();
    processScreenshot();
  }
});

console.log('Screenshot to Audio frontend initialized');
console.log('Press F9 or click the button to capture a screenshot');

// Check backend health on startup
async function checkBackendHealth() {
  try {
    const response = await axios.get(HEALTH_URL, { timeout: 5000 });
    console.log('Backend health:', response.data);
  } catch (error) {
    console.warn('Could not reach backend health endpoint:', error);
  }
}

checkBackendHealth();
