import React from 'react';
import styles from './Header.module.css';
import { useTheme } from '../../context/ThemeContext';
import { useWorkflow } from '../../context/WorkflowContext';

const Header = () => {
  const { theme, toggleTheme } = useTheme();
  const { tasks } = useWorkflow();

  const total = tasks.length;
  const completed = tasks.filter(t => t.status === 'Completed').length;
  const isAllComplete = total > 0 && total === completed;

  return (
    <header className={`${styles.header} glass-panel`}>
      <div className={styles.brand}>
        <div className={styles.logo}>P0</div>
        <div>
          <h1 className={styles.title}>Project0</h1>
          <p className={styles.subtitle}>Workflow Management Dashboard</p>
        </div>
      </div>
      
      <div className={styles.actions}>
        <div className={`${styles.statusBadge} ${!isAllComplete ? styles.inProgress : ''}`}>
          {isAllComplete ? 'All Systems Go' : 'Work in Progress'}
        </div>
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
