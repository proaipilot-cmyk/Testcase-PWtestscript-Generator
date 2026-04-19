// Fetch actual data from our Vite backend plugin
export const fetchTasks = async () => {
  const response = await fetch('/api/progress');
  if (!response.ok) throw new Error('Network response was not ok');
  const data = await response.json();
  return data.tasks;
};

export const fetchLogs = async () => {
  const response = await fetch('/api/progress');
  if (!response.ok) throw new Error('Network response was not ok');
  const data = await response.json();
  return data.logs;
};

export const updateTaskStatus = async (id, newStatus) => {
  // Read-only visualization in this scenario
  // To make it actual, we could trigger a python script from the backend
  console.log('Update task not fully implemented: backend read-only', id, newStatus);
  return { id, status: newStatus };
};
