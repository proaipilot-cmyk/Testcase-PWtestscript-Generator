import React from 'react';
import styles from './Workflow.module.css';
import { useWorkflow } from '../../context/WorkflowContext';
import LoadingSpinner from '../LoadingSpinner/LoadingSpinner';

const Workflow = () => {
  const { tasks, currentStage, loading } = useWorkflow();

  if (tasks.length === 0) {
    return (
      <div className={`${styles.workflowContainer} glass-panel`}>
        <h2 className={styles.title}>Pipeline Pipeline</h2>
        <p>No active pipeline data.</p>
      </div>
    );
  }
  
  const completed = tasks.filter(t => t.status === 'Completed').length;
  const percentage = Math.round((completed / tasks.length) * 100);
  const isProcessing = currentStage !== 'Idle' && currentStage !== 'Error';

  return (
    <>
      <LoadingSpinner isVisible={isProcessing} progress={percentage} />
      <div className={`${styles.workflowContainer} glass-panel`}>
        <div className={styles.header}>
          <div>
            <h2 className={styles.title}>Conversion Pipeline</h2>
            <p className={styles.subtitle}>Track progress from CSV to Git deployment</p>
          </div>
          <div className={styles.stats}>
             <span className={styles.progressText}>{percentage}% Complete</span>
             <div className={styles.miniProgress}>
               <div className={styles.miniBar} style={{ width: `${percentage}%` }}></div>
             </div>
          </div>
        </div>

        <div className={styles.stepper}>
          {tasks.map((task, index) => {
            const isCompleted = task.status === 'Completed';
            const isCurrent = task.status === 'In Progress' || currentStage === task.name;
            
            return (
              <div key={task.id} className={`${styles.step} ${isCompleted ? styles.completed : ''} ${isCurrent ? styles.active : ''}`}>
                <div className={styles.stepHeader}>
                  <div className={styles.circle}>
                    {isCompleted ? '✓' : index + 1}
                  </div>
                  <div className={styles.line}></div>
                </div>
                <div className={styles.labelContainer}>
                  <span className={styles.label}>{task.name}</span>
                  <span className={styles.status}>{task.status}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
};

export default Workflow;
