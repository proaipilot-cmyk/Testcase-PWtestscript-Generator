import React from 'react';
import styles from './Workflow.module.css';
import { useWorkflow } from '../../context/WorkflowContext';

const Workflow = () => {
  const { tasks, loadingTasks, refreshData } = useWorkflow();

  if (loadingTasks || tasks.length === 0) {
    return (
      <div className={`${styles.workflowContainer} glass-panel`}>
        <div className={styles.header}>
          <h2 className={styles.title}>Pipeline Progress</h2>
        </div>
        <p>Loading pipeline data...</p>
      </div>
    );
  }
  
  const completed = tasks.filter(t => t.status === 'Completed').length;
  const percentage = Math.round((completed / tasks.length) * 100);

  // Directly map the tasks to our stepper phases
  const phases = tasks.map((t, index) => {
    // Determine status purely from the task status for simplicity
    let statusId = 'pending';
    if (t.status === 'Completed') statusId = 'completed';
    if (t.status === 'In Progress') statusId = 'inProgress';
    
    // Shorten the labels
    let label = t.name;
    if (t.name.includes('Parser')) label = 'Parse';
    if (t.name.includes('Planner')) label = 'Plan';
    if (t.name.includes('Generator')) label = 'Generate';
    if (t.name.includes('Validator')) label = 'Validate';

    return {
      id: index + 1,
      label,
      statusId
    };
  });

  return (
    <div className={`${styles.workflowContainer} glass-panel`}>
      <div className={styles.header}>
        <h2 className={styles.title}>Conversion Pipeline Progress</h2>
        <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
           <span className={styles.progressText}>{percentage}% Completed ({completed}/{tasks.length} steps)</span>
           <button 
             onClick={refreshData} 
             style={{padding: '0.25rem 0.75rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem'}}
           >
             Refresh
           </button>
        </div>
      </div>

      <div className={styles.stepper}>
        <div 
          className={styles.progressLine} 
          style={{ width: `${percentage}%` }}
        ></div>
        
        {phases.map((phase) => (
          <div key={phase.id} className={`${styles.step} ${styles[phase.statusId]}`}>
            <div className={styles.circle}>
              {phase.statusId === 'completed' ? '✓' : phase.id}
            </div>
            <span className={styles.label}>{phase.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Workflow;
