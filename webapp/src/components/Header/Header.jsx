import React from 'react';
import styles from './Header.module.css';
import { useTheme } from '../../context/ThemeContext';
import { useWorkflow } from '../../context/WorkflowContext';

const Header = () => {
  const { theme, toggleTheme } = useTheme();
  const { tasks, currentStage, handleReset } = useWorkflow();

  const stages = [
    { name: 'Parser', id: '1' },
    { name: 'Planner', id: '2' },
    { name: 'Generator', id: '3' },
    { name: 'Run', id: '4' },
    { name: 'Git Push', id: '5' }
  ];

  const onReset = () => {
    if (window.confirm('Are you sure you want to reset all workflow progress?')) {
      handleReset();
    }
  };

  return (
    <header className={`${styles.header} glass-panel`}>
      <div className={styles.brand}>
        <div className={styles.logo}>P0</div>
        <h1 className={styles.title}>AutoTest Dashboard</h1>
      </div>
      
      <div className={styles.stageBanner}>
        {stages.map((stage, index) => {
          const task = tasks.find(t => t.id === stage.id);
          const isCurrent = currentStage === stage.name;
          const isCompleted = task?.status === 'Completed';
          
          return (
            <React.Fragment key={stage.id}>
              <div className={`${styles.stageItem} ${isCurrent ? styles.active : ''} ${isCompleted ? styles.completed : ''}`}>
                <div className={styles.stageDot}></div>
                <span>{stage.name}</span>
              </div>
              {index < stages.length - 1 && <div className={styles.connector}></div>}
            </React.Fragment>
          );
        })}
      </div>

      <div className={styles.actions}>
        <button 
          className={styles.resetBtn}
          onClick={onReset}
          title="Reset all workflow progress"
          aria-label="Reset Workflow"
        >
          🔄
        </button>
        <button 
          className={styles.themeToggle} 
          onClick={toggleTheme}
          aria-label="Toggle Theme"
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
      </div>
    </header>
  );
};

export default Header;
