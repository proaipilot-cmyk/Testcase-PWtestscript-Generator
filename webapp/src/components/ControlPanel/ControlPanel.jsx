import React from 'react';
import styles from './ControlPanel.module.css';
import { useWorkflow } from '../../context/WorkflowContext';

const ControlPanel = () => {
  const { handleRun, currentStage, tasks } = useWorkflow();

  const generatorTask = tasks.find(t => t.id === '3');
  const runTask = tasks.find(t => t.id === '4');
  
  const isReadyToRun = generatorTask?.status === 'Completed' && currentStage === 'Idle';
  const isRunning = runTask?.status === 'In Progress';
  
  // Calculate progress for test execution
  const getRunProgress = () => {
    if (isRunning) return 50; // Mid-progress during execution
    if (runTask?.status === 'Completed') return 100;
    return 0;
  };

  return (
    <div className={`${styles.container} glass-panel`}>
      <div className={styles.info}>
        <h3 className={styles.title}>Execution Controls</h3>
        <p className={styles.desc}>Run the generated POM framework to verify test cases.</p>
      </div>
      
      <button 
        className={`${styles.runBtn} primary-button`}
        onClick={handleRun}
        disabled={!isReadyToRun}
        title={!isReadyToRun ? 'Complete generation step first' : 'Start test execution'}
      >
        <div 
          className={`${styles.progressBar} ${isRunning ? styles.active : ''}`}
          style={{ width: `${getRunProgress()}%` }}
        />
        <div className={styles.buttonContent}>
          <span className={styles.icon}>▶️</span>
          <span>{isRunning ? 'Running Tests...' : 'Run Automation'}</span>
        </div>
      </button>
      
      {!isReadyToRun && (
        <span className={styles.warning}>
          {generatorTask?.status !== 'Completed' 
            ? 'Generation must complete first' 
            : currentStage !== 'Idle' 
            ? 'Pipeline is currently processing'
            : 'Upload a file to start'}
        </span>
      )}
    </div>
  );
};

export default ControlPanel;
