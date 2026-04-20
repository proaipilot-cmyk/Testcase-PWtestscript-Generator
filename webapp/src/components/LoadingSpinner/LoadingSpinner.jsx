import React from 'react';
import styles from './LoadingSpinner.module.css';

const LoadingSpinner = ({ isVisible, progress = 0 }) => {
  if (!isVisible) return null;

  return (
    <div className={styles.overlay} role="status" aria-live="polite">
      <div className={styles.container}>
        <div className={styles.loadingBox}>
          <h2 className={styles.text}>Loading...</h2>
          <div className={styles.progressBarContainer}>
            <div 
              className={styles.progressBar}
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
              role="progressbar"
              aria-valuenow={Math.round(progress)}
              aria-valuemin="0"
              aria-valuemax="100"
            >
              <div className={styles.shimmer}></div>
            </div>
          </div>
          <p className={styles.percentage}>{Math.round(Math.min(100, Math.max(0, progress)))}%</p>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
