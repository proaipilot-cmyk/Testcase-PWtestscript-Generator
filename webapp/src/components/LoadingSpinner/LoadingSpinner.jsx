import React from 'react';
import styles from './LoadingSpinner.module.css';

const LoadingSpinner = ({ isVisible, progress = 0 }) => {
  if (!isVisible) return null;

  return (
    <div className={styles.overlay}>
      <div className={styles.container}>
        <div className={styles.loadingBox}>
          <h2 className={styles.text}>Loading...</h2>
          <div className={styles.progressBarContainer}>
            <div 
              className={styles.progressBar}
              style={{ width: `${progress}%` }}
            >
              <div className={styles.shimmer}></div>
            </div>
          </div>
          <p className={styles.percentage}>{Math.round(progress)}%</p>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
