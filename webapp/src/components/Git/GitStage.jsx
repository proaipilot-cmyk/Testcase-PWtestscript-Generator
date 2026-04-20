import React, { useState } from 'react';
import styles from './GitStage.module.css';
import { useWorkflow } from '../../context/WorkflowContext';

const GitStage = () => {
  const { handleGitPush, currentStage, tasks } = useWorkflow();
  const [url, setUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [token, setToken] = useState('');
  const [selectedFile, setSelectedFile] = useState('tests/test_automation.py');

  const runTask = tasks.find(t => t.id === '4');
  const gitTask = tasks.find(t => t.id === '5');
  
  const isReadyToPush = runTask?.status === 'Completed' && currentStage === 'Idle';
  const isPushing = gitTask?.status === 'In Progress';
  
  // Calculate progress for git push
  const getPushProgress = () => {
    if (isPushing) return 60; // Mid-progress during push
    if (gitTask?.status === 'Completed') return 100;
    return 0;
  };

  const onPush = () => {
    if (!url.trim()) {
      alert('Please enter a Git URL');
      return;
    }
    if (!branch.trim()) {
      alert('Please enter a branch name');
      return;
    }
    
    handleGitPush({ 
      url: url.trim(), 
      branch: branch.trim(), 
      token: token.trim(), 
      files: [selectedFile] 
    });
  };

  return (
    <div className={`${styles.container} glass-panel`}>
      <h3 className={styles.title}>Deploy Framework</h3>
      <div className={styles.inputGrid}>
        <div className={styles.inputGroup}>
          <label>Git Repository URL</label>
          <input 
            type="text" 
            value={url} 
            onChange={(e) => setUrl(e.target.value)} 
            placeholder="https://github.com/user/repo.git"
            className={styles.input}
            disabled={!isReadyToPush}
          />
        </div>

        <div className={styles.inputGroup}>
          <label>Target Branch</label>
          <input 
            type="text" 
            value={branch} 
            onChange={(e) => setBranch(e.target.value)} 
            placeholder="main"
            className={styles.input}
            disabled={!isReadyToPush}
          />
        </div>
      </div>

      <div className={styles.inputGroup}>
        <label>Personal Access Token (optional for public repo)</label>
        <input 
          type="password" 
          value={token} 
          onChange={(e) => setToken(e.target.value)} 
          placeholder="ghp_xxxxxxxxxxxx"
          className={styles.input}
          disabled={!isReadyToPush}
        />
      </div>

      <div className={styles.inputGroup}>
        <label>Select Target for Push</label>
        <select 
          value={selectedFile} 
          onChange={(e) => setSelectedFile(e.target.value)}
          className={styles.select}
          disabled={!isReadyToPush}
        >
          <option value="tests/test_automation.py">tests/test_automation.py</option>
          <option value="tests/pages/">Pages Object folder</option>
          <option value="all">Full Framework</option>
        </select>
      </div>

      <button 
        className={`${styles.pushBtn} primary-button`}
        onClick={onPush}
        disabled={!isReadyToPush}
        title={!isReadyToPush ? 'Complete automation run first' : 'Deploy to Git'}
      >
        <div 
          className={`${styles.progressBar} ${isPushing ? styles.active : ''}`}
          style={{ width: `${getPushProgress()}%` }}
        />
        <div className={styles.buttonContent}>
          <span className={styles.icon}>🚀</span>
          <span>{isPushing ? 'Pushing...' : 'Push to Git'}</span>
        </div>
      </button>

      <div className={styles.info}>
        <p>Deployment will add, commit, and push selected files to the target branch.</p>
        {!isReadyToPush && (
          <p style={{ marginTop: '8px', color: '#ff9f1c' }}>
            ⚠️ {runTask?.status !== 'Completed' 
              ? 'Complete automation run first' 
              : currentStage !== 'Idle' 
              ? 'Pipeline is currently processing'
              : 'Start the process with upload'}
          </p>
        )}
      </div>
    </div>
  );
};

export default GitStage;
