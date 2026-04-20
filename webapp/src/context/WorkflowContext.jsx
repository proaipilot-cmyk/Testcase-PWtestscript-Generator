import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import { fetchProgress, uploadFile, runTests, pushToGit, clearLogs, resetWorkflow } from '../services/api';

const WorkflowContext = createContext();

export const useWorkflow = () => useContext(WorkflowContext);

export const WorkflowProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [logs, setLogs] = useState([]);
  const [currentStage, setCurrentStage] = useState('Idle');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const pollingRef = useRef(null);

  const loadData = useCallback(async () => {
    try {
      const data = await fetchProgress();
      setTasks(data.tasks);
      setLogs(data.logs);
      setCurrentStage(data.current_stage || 'Idle');
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    pollingRef.current = setInterval(loadData, 2000);
    return () => clearInterval(pollingRef.current);
  }, [loadData]);

  const handleUpload = async (file) => {
    try {
      setLoading(true);
      setError(null);
      const response = await uploadFile(file);
      if (response.error) {
        setError('Upload failed: ' + response.error);
      }
      await loadData();
    } catch (err) {
      setError('Upload failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRun = async () => {
    try {
      setError(null);
      const response = await runTests();
      if (response.error) {
        setError('Run failed: ' + response.error);
      }
      await loadData();
    } catch (err) {
      setError('Run failed: ' + err.message);
    }
  };

  const handleGitPush = async (gitData) => {
    try {
      setError(null);
      // Validate Git URL before pushing
      if (!gitData.url) {
        setError('Git URL is required');
        return;
      }
      const response = await pushToGit(gitData);
      if (response.error) {
        setError('Git push failed: ' + response.error);
      }
      await loadData();
    } catch (err) {
      setError('Git push failed: ' + err.message);
    }
  };

  const handleClearLogs = async () => {
    try {
      setError(null);
      await clearLogs();
      await loadData();
    } catch (err) {
      setError('Failed to clear logs: ' + err.message);
    }
  };

  const handleReset = async () => {
    try {
      setError(null);
      await resetWorkflow();
      await loadData();
    } catch (err) {
      setError('Failed to reset workflow: ' + err.message);
    }
  };

  return (
    <WorkflowContext.Provider value={{
      tasks,
      logs,
      currentStage,
      loading,
      error,
      handleUpload,
      handleRun,
      handleGitPush,
      handleClearLogs,
      handleReset,
      refreshData: loadData
    }}>
      {children}
    </WorkflowContext.Provider>
  );
};
