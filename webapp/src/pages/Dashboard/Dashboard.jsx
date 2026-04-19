import React from 'react';
import Header from '../../components/Header/Header';
import Workflow from '../../components/Workflow/Workflow';
import TaskList from '../../components/TaskList/TaskList';
import Logs from '../../components/Logs/Logs';
import styles from './Dashboard.module.css';
import { useWorkflow } from '../../context/WorkflowContext';

const Dashboard = () => {
  const { error, refreshData } = useWorkflow();

  return (
    <>
      <Header />
      <div className={styles.dashboardLayout}>
        {error && (
          <div style={{ padding: '1rem', background: '#fee2e2', color: '#b91c1c', borderRadius: '8px', marginBottom: '1rem' }}>
            <p>{error}</p>
            <button onClick={refreshData} style={{ marginTop: '0.5rem', padding: '0.5rem 1rem', background: '#b91c1c', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Retry</button>
          </div>
        )}
        
        <Workflow />
        
        <div className={styles.mainContent}>
          <TaskList />
          <Logs />
        </div>
      </div>
    </>
  );
};

export default Dashboard;
