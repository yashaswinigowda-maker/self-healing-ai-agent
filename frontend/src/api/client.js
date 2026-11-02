const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // System Health & Settings
  getHealth: () => request('/health'),
  getSettings: () => request('/settings'),
  updateSettings: (data) => request('/settings', { method: 'POST', body: JSON.stringify(data) }),

  // Dashboard & Statistics
  getDashboardStats: () => request('/dashboard/stats'),

  // Tasks Execution
  createTask: (title, description, forceFault = null) =>
    request('/tasks', {
      method: 'POST',
      body: JSON.stringify({
        title,
        description,
        force_fault: forceFault || null,
      }),
    }),

  executeTask: (taskId) =>
    request(`/tasks/${taskId}/execute`, {
      method: 'POST',
    }),

  getTaskDetails: (taskId) => request(`/tasks/${taskId}`),
  getTaskStatus: (taskId) => request(`/tasks/${taskId}/status`),
  listTasks: (status = null) => {
    const q = status ? `?status=${encodeURIComponent(status)}` : '';
    return request(`/tasks${q}`);
  },

  // Recovery Monitoring
  getRecoveryHistory: () => request('/recovery/history'),

  // Episodic Memory
  getMemories: (type = null, query = null) => {
    const params = new URLSearchParams();
    if (type) params.append('memory_type', type);
    if (query) params.append('query', query);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request(`/memories${qs}`);
  },

  // Failure Predictions
  getPredictions: () => request('/predictions'),
};
