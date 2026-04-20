import React, { useRef } from 'react';
import styles from './Sidebar.module.css';
import { useWorkflow } from '../../context/WorkflowContext';

const Sidebar = () => {
  const { handleUpload, currentStage, tasks } = useWorkflow();
  const fileInputRef = useRef(null);

  const uploadTask = tasks.find(t => t.id === '1');
  const isProcessing = currentStage !== 'Idle';
  const isUploading = uploadTask?.status === 'In Progress';
  
  // Calculate progress for upload task
  const getUploadProgress = () => {
    if (isUploading) return 33; // Estimated progress during upload
    if (uploadTask?.status === 'Completed') return 100;
    return 0;
  };

  const onUploadClick = () => {
    fileInputRef.current.click();
  };

  const onFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleUpload(file);
    }
  };

  return (
    <aside className={`${styles.sidebar} glass-panel`}>
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Processing</h3>
        <button 
          className={`${styles.uploadBtn} primary-button`}
          onClick={onUploadClick}
          disabled={isProcessing}
          title={isProcessing ? 'Wait for current process to complete' : 'Upload a test file'}
        >
          <div 
            className={`${styles.progressBar} ${isUploading ? styles.active : ''}`}
            style={{ width: `${getUploadProgress()}%` }}
          />
          <div className={styles.buttonContent}>
            <span className={styles.icon}>📤</span>
            <span>{isUploading ? 'Uploading...' : 'Upload Test File'}</span>
          </div>
        </button>
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={onFileChange}
          accept=".csv,.xlsx,.json"
        />
        <p className={styles.hint}>Supported formats: .csv, .xlsx, .json</p>
      </div>

      <div className={styles.divider}></div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Help & Resources</h3>
        <ul className={styles.menuList}>
          <li><span className={styles.icon}>📖</span> Documentation</li>
          <li><span className={styles.icon}>🛠️</span> Settings</li>
          <li><span className={styles.icon}>💬</span> Support</li>
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar;
