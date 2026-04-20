// Fetch actual data from our backend
export const fetchProgress = async () => {
  const response = await fetch('/api/progress');
  if (!response.ok) throw new Error('Network response was not ok');
  return await response.json();
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Upload failed');
  return await response.json();
};

export const runTests = async () => {
  const response = await fetch('/api/run', { method: 'POST' });
  if (!response.ok) throw new Error('Failed to run tests');
  return await response.json();
};

export const pushToGit = async (gitData) => {
  const response = await fetch('/api/push-to-git', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(gitData),
  });
  if (!response.ok) throw new Error('Git push failed');
  return await response.json();
};

export const clearLogs = async () => {
  const response = await fetch('/api/clear-log', { method: 'POST' });
  if (!response.ok) throw new Error('Failed to clear logs');
  return await response.json();
};

export const resetWorkflow = async () => {
  const response = await fetch('/api/reset', { method: 'POST' });
  if (!response.ok) throw new Error('Failed to reset workflow');
  return await response.json();
};
