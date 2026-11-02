import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import TaskExecution from './pages/TaskExecution';
import RecoveryMonitoring from './pages/RecoveryMonitoring';
import MemoryManagement from './pages/MemoryManagement';
import FailurePrediction from './pages/FailurePrediction';
import TaskHistory from './pages/TaskHistory';
import Settings from './pages/Settings';
import { api } from './api/client';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedTaskId, setSelectedTaskId] = useState(null);
  const [isOnline, setIsOnline] = useState(true);
  const [geminiConfigured, setGeminiConfigured] = useState(false);
  const [recoveryRate, setRecoveryRate] = useState(100);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const checkHealth = async () => {
    try {
      setIsRefreshing(true);
      const data = await api.getHealth();
      setIsOnline(data.status === 'healthy');
      setGeminiConfigured(Boolean(data.gemini_configured));

      const stats = await api.getDashboardStats().catch(() => null);
      if (stats && stats.recovery_success_rate !== undefined) {
        setRecoveryRate(stats.recovery_success_rate);
      }
    } catch (err) {
      setIsOnline(false);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getPageTitle = () => {
    switch (activePage) {
      case 'dashboard':
        return { title: 'Executive Overview', subtitle: 'Self-healing multi-step execution metrics and real-time status' };
      case 'execute':
        return { title: 'Task Planning & Execution', subtitle: 'Decompose, execute, verify, and auto-heal automated workflows' };
      case 'recovery':
        return { title: 'Recovery Monitoring', subtitle: 'Detailed error diagnostics, strategy selections, and validation logs' };
      case 'memory':
        return { title: 'Episodic Memory Management', subtitle: 'Experience catalog for learning from previous successes and failures' };
      case 'prediction':
        return { title: 'Failure Pattern Prediction', subtitle: 'Pre-execution risk scoring and vulnerability interception' };
      case 'history':
        return { title: 'Task History & Audits', subtitle: 'Comprehensive audit log of all completed, recovered, and failed tasks' };
      case 'settings':
        return { title: 'Framework Settings', subtitle: 'Google Gemini AI models, API keys, thresholds, and sandbox allowlist' };
      default:
        return { title: 'Self-Healing AI Agent', subtitle: 'Autonomous Execution Framework' };
    }
  };

  const headerInfo = getPageTitle();

  return (
    <div className="app-container">
      <Sidebar
        activePage={activePage}
        setActivePage={(page) => {
          setActivePage(page);
          if (page !== 'history') {
            setSelectedTaskId(null);
          }
        }}
        isOnline={isOnline}
        geminiConfigured={geminiConfigured}
      />

      <div className="main-content">
        <Header
          title={headerInfo.title}
          subtitle={headerInfo.subtitle}
          onRefresh={checkHealth}
          isRefreshing={isRefreshing}
          recoveryRate={recoveryRate}
        />

        <main style={{ flex: 1 }}>
          {activePage === 'dashboard' && (
            <Dashboard setActivePage={setActivePage} setSelectedTaskId={setSelectedTaskId} />
          )}
          {activePage === 'execute' && (
            <TaskExecution setActivePage={setActivePage} setSelectedTaskId={setSelectedTaskId} />
          )}
          {activePage === 'recovery' && <RecoveryMonitoring />}
          {activePage === 'memory' && <MemoryManagement />}
          {activePage === 'prediction' && <FailurePrediction />}
          {activePage === 'history' && (
            <TaskHistory selectedTaskId={selectedTaskId} setSelectedTaskId={setSelectedTaskId} />
          )}
          {activePage === 'settings' && <Settings />}
        </main>
      </div>
    </div>
  );
}
