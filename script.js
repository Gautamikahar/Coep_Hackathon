const form = document.getElementById('uploadForm');
const chatContainer = document.getElementById('chatContainer');

function addMessage(text, sender) {
  const msg = document.createElement('div');
  msg.classList.add('message', sender);
  msg.textContent = text;
  chatContainer.appendChild(msg);
  chatContainer.scrollTop = chatContainer.scrollHeight; // auto scroll
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById('csvFile');
  if (!fileInput.files.length) return;

  // Show user message
  addMessage(`Uploading CSV: ${fileInput.files[0].name}`, 'user');

  const formData = new FormData();
  formData.append('csvFile', fileInput.files[0]);

  addMessage('Analyzing data...', 'ai');

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      body: formData
    });

    const result = await response.json();

    // Remove "Analyzing..." message
    chatContainer.lastChild.remove();

    // Show analysis
    addMessage(`Total Negative Feedback: ${result.analysis.total_negative}`, 'ai');
    addMessage(`Feature Breakdown: ${JSON.stringify(result.analysis.feature_breakdown, null, 2)}`, 'ai');
    addMessage(`Cost Estimates: ${JSON.stringify(result.analysis.cost_by_feature, null, 2)}`, 'ai');

    // Show AI strategy
    addMessage(`AI Strategy: ${result.ai_strategy}`, 'ai');

  } catch (err) {
    addMessage(`Error: ${err.message}`, 'ai');
  }
});
