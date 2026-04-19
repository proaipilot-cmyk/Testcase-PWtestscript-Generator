import React from 'react';
import styles from './TaskList.module.css';
import { useWorkflow } from '../../context/WorkflowContext';

const TaskList = () => {
  const { tasks, loadingTasks, updateTask } = useWorkflow();

  const getStatusClass = (status) => {
    switch(status) {
      case 'Completed': return styles.statusCompleted;
      case 'In Progress': return styles.statusInProgress;
      case 'Blocked': return styles.statusBlocked;
      default: return styles.statusPending;
    }
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleString(undefined, { 
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  const handleStatusChange = (id, e) => {
    updateTask(id, e.target.value);
  };

  if (loadingTasks) {
    return (
      <div className={`${styles.listContainer} glass-panel`}>
        <h2 className={styles.title}>Tasks</h2>
        <p>Loading tasks...</p>
      </div>
    );
  }

  return (
    <div className={`${styles.listContainer} glass-panel`}>
      <div className={styles.header}>
        <h2 className={styles.title}>Tasks</h2>
      </div>
      
      {tasks.length === 0 ? (
        <p className={styles.taskMeta}>No tasks available.</p>
      ) : (
        <ul className={styles.taskList}>
          {tasks.map(task => (
            <li key={task.id} className={styles.taskItem}>
              <div className={styles.taskInfo}>
                <span className={styles.taskName}>{task.name}</span>
                <span className={styles.taskMeta}>Updated: {formatDate(task.lastUpdated)}</span>
              </div>
              
              <div className={styles.taskActions}>
                <div className={`${styles.statusIndicator} ${getStatusClass(task.status)}`}>
                  <span className={styles.dot}></span>
                </div>
                
                <select 
                  className={styles.select} 
                  value={task.status}
                  onChange={(e) => handleStatusChange(task.id, e)}
                >
                  <option value="Pending">Pending</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                  <option value="Blocked">Blocked</option>
                </select>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TaskList;
