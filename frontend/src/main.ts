import axios from 'axios';

const ORCHESTRATOR_URL = '/api/process';
const HEALTH_URL = '/api/health';

const captureBtn = document.getElementById('captureBtn') as HTMLButtonElement;
const processingSection = document.getElementById('processingSection') as HTMLDivElement;
const resultsSection = document.getElementById('resultsSection') as HTMLDivElement;
const errorMessage = document.getElementById('errorMessage') as HTMLDivElement;
const previewSection = document.getElementById('previewSection') as HTMLDivElement;
const previewImage = document.getElementById('previewImage') as HTMLImageElement;
const captionText = document.getElementById('captionText') as HTMLDivElement;
const audioPlayer = document.getElementById('audioPlayer') as HTMLAudioElement;

const step1Icon = document.getElementById('step1Icon') as HTMLDivElement;
const step2Icon = document.getElementById('step2Icon') as HTMLDivElement;
const step3Icon = document.getElementById('step3Icon') as HTMLDivElement;

interface ProcessingStep {
  icon: HTMLDivElement;
  status: 'pending' | 'processing' | 'complete' | 'error';
}

const steps: ProcessingStep[] = [
  { icon: step1Icon, status: 'pending' },
  { icon: step2Icon, status: 'pending' },
  { icon: step3Icon, status: 'pending' }
];

function updateStepStatus(stepIndex: number, status: 'pending' | 'processing' | 'complete' | 'error') {
  const step = steps[stepIndex];
  step.status = status;
  
  step.icon.className = `step-icon ${status}`;
  
  if (status === 'complete') {
    step.icon.textContent = '✓';
  } else if (status === 'error') {
    step.icon.textContent = '✕';
  } else {
    step.icon.textContent = (stepIndex + 1).toString();
  }
}

function resetSteps() {
  steps.forEach((_, index) => updateStepStatus(index, 'pending'));
}

function showError(message: string) {
  errorMessage.textContent = message;
  errorMessage.classList.add('show');
  setTimeout(() => {
    errorMessage.classList.remove('show');
  }, 5000);
}

function hideResults() {
  resultsSection.classList.remove('show');
  previewSection.classList.remove('show');
  processingSection.classList.remove('show');
}

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

async function sendToOrchestrator(imageBlob: Blob): Promise<{ audio: Blob; caption: string }> {
  const formData = new FormData();
  formData.append('file', imageBlob, 'screenshot.png');

  const response = await axios.post(ORCHESTRATOR_URL, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    responseType: 'blob',
    timeout: 120000
  });

  const caption = response.headers['x-caption-text'] || 'No caption available';
  
  return {
    audio: response.data,
    caption: caption
  };
}

async function processScreenshot() {
  captureBtn.disabled = true;
  hideResults();
  resetSteps();
  processingSection.classList.add('show');

  try {
    updateStepStatus(0, 'processing');
    const imageBlob = await captureScreenshot();
    updateStepStatus(0, 'complete');

    const imageUrl = URL.createObjectURL(imageBlob);
    previewImage.src = imageUrl;
    previewSection.classList.add('show');

    updateStepStatus(1, 'processing');
    updateStepStatus(2, 'processing');
    
    const result = await sendToOrchestrator(imageBlob);
    
    updateStepStatus(1, 'complete');
    updateStepStatus(2, 'complete');

    captionText.textContent = result.caption;
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

captureBtn.addEventListener('click', processScreenshot);

document.addEventListener('keydown', (event) => {
  if (event.key === 'F9' && !captureBtn.disabled) {
    event.preventDefault();
    processScreenshot();
  }
});

console.log('Screenshot to Audio frontend initialized');
console.log('Press F9 or click the button to capture a screenshot');

async function checkBackendHealth() {
  try {
    const response = await axios.get(HEALTH_URL, { timeout: 5000 });
    console.log('Backend health:', response.data);
  } catch (error) {
    console.warn('Could not reach backend health endpoint:', error);
  }
}

checkBackendHealth();
