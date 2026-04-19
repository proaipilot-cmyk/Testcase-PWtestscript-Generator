import React from 'react';
import Dashboard from './pages/Dashboard/Dashboard';
import { ThemeProvider } from './context/ThemeContext';
import { WorkflowProvider } from './context/WorkflowContext';

function App() {
  return (
    <ThemeProvider>
      <WorkflowProvider>
        <div className="app-background">
          <Dashboard />
        </div>
      </WorkflowProvider>
    </ThemeProvider>
  );
}

export default App;
