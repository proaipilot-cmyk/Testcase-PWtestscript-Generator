import React from 'react';
import Header from '../../components/Header/Header';
import Sidebar from '../../components/Sidebar/Sidebar';
import Workflow from '../../components/Workflow/Workflow';
import ControlPanel from '../../components/ControlPanel/ControlPanel';
import GitStage from '../../components/Git/GitStage';
import Logs from '../../components/Logs/Logs';
import styles from './Dashboard.module.css';
import { useWorkflow } from '../../context/WorkflowContext';

const Dashboard = () => {
  const { error, refreshData } = useWorkflow();

  return (
    <div className={styles.appWrapper}>
      <Header />
      <div className={styles.dashboardLayout}>
        <Sidebar />
        
        <main className={styles.mainContent}>
          {error && (
            <div className={styles.errorBanner}>
              <p>{error}</p>
              <button onClick={refreshData}>Retry</button>
            </div>
          )}
          
          <Workflow />
          
          <div className={styles.actionsGrid}>
            <div className={styles.column}>
              <ControlPanel />
              <GitStage />
            </div>
            <div className={styles.column}>
              <Logs />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
