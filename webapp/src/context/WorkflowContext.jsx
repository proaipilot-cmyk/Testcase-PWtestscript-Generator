import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { fetchTasks, updateTaskStatus, fetchLogs } from '../services/api';

const WorkflowContext = createContext();

export const useWorkflow = () => useContext(WorkflowContext);

export const WorkflowProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    try {
      setLoadingTasks(true);
      setLoadingLogs(true);
      const [fetchedTasks, fetchedLogs] = await Promise.all([
        fetchTasks(),
        fetchLogs()
      ]);
      setTasks(fetchedTasks);
      setLogs(fetchedLogs);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoadingTasks(false);
      setLoadingLogs(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const updateTask = async (id, newStatus) => {
    // Optimistic UI update
    const previousTasks = [...tasks];
    const previousLogs = [...logs];
    
    setTasks(tasks.map(t => t.id === id ? { ...t, status: newStatus, lastUpdated: new Date().toISOString() } : t));
    
    // Optimistically add log
    const taskName = tasks.find(t => t.id === id)?.name;
    setLogs([{
      id: `temp-${Date.now()}`,
      message: `${taskName} marked as ${newStatus}`,
      time: new Date().toISOString()
    }, ...logs]);

    try {
      // API call
      await updateTaskStatus(id, newStatus);
      // We could refetch logs here but we already optimistically updated
      // A more robust app would fetch the real updated log list
      const updatedLogs = await fetchLogs();
      setLogs(updatedLogs);
    } catch (err) {
      // Revert on error
      setTasks(previousTasks);
      setLogs(previousLogs);
      setError('Failed to update task. Changes reverted.');
    }
  };

  return (
    <WorkflowContext.Provider value={{
      tasks,
      logs,
      loadingTasks,
      loadingLogs,
      error,
      updateTask,
      refreshData: loadData
    }}>
      {children}
    </WorkflowContext.Provider>
  );
};
