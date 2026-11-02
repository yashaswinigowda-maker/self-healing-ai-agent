import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import {
  Settings as SettingsIcon,
  Key,
  Cpu,
  Shield,
  Sliders,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Save,
} from 'lucide-react';

export default function Settings() {
  const [settingsData, setSettingsData] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gemini-2.5-flash');
  const [maxRecovery, setMaxRecovery] = useState(3);
  const [maxReplan, setMaxReplan] = useState(2);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.65);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState(null);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getSettings();
      setSettingsData(data);
      setModel(data.gemini_model || 'gemini-2.5-flash');
      setMaxRecovery(data.max_recovery_attempts || 3);
      setMaxReplan(data.max_replan_attempts || 2);
      setConfidenceThreshold(data.confidence_threshold || 0.65);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      setSaveSuccess(false);
      setError(null);

      const payload = {
        model,
        max_recovery_attempts: parseInt(maxRecovery, 10),
        max_replan_attempts: parseInt(maxReplan, 10),
        confidence_threshold: parseFloat(confidenceThreshold),
      };

      if (apiKey.trim()) {
        payload.api_key = apiKey.trim();
      }

      const updated = await api.updateSettings(payload);
      setSettingsData(updated);
      setSaveSuccess(true);
      setApiKey(''); // Clear secret from form after saving
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading && !settingsData) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <RefreshCw size={28} className="spin-animate" color="var(--accent-indigo)" />
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>Framework Settings & Configuration</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Configure Google Gemini AI credentials, dynamic replan thresholds, recovery safety constraints, and tool sandbox boundaries.
        </p>
      </div>

      {saveSuccess && (
        <div style={{ padding: '1rem', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', color: '#34d399', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CheckCircle size={18} />
          <span>Settings successfully updated in runtime engine!</span>
        </div>
      )}

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#fb7185', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Gemini AI Configuration */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', color: 'var(--accent-indigo)' }}>
            <Key size={20} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>Google Gemini AI Configuration</h3>
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                Gemini API Key
              </label>
              <span style={{ fontSize: '0.78rem', color: settingsData?.api_key_configured ? '#34d399' : '#f59e0b', fontWeight: 600 }}>
                {settingsData?.api_key_configured ? '✓ Key Configured in Backend' : '⚠ Missing / Unset (Using Deterministic Engine)'}
              </span>
            </div>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={settingsData?.api_key_configured ? '•••••••••••••••••••••••••••• (Leave blank to keep existing)' : 'Enter your Google Gemini API key...'}
              className="input-field font-mono"
            />
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              Your key is stored securely in backend server memory and is never exposed in browser payloads.
            </p>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600, marginBottom: '0.35rem' }}>
              Model Architecture
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="select-field"
            >
              <option value="gemini-2.5-flash">Gemini 2.5 Flash (Recommended: Fast & Structured)</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep Reasoning & Complex Re-planning)</option>
              <option value="gemini-1.5-flash">Gemini 1.5 Flash (Lightweight Automation)</option>
            </select>
          </div>
        </div>

        {/* Self-Healing Control Limits */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', color: 'var(--accent-cyan)' }}>
            <Sliders size={20} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>Self-Healing Safety & Convergence Thresholds</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Max Recovery Attempts per Step
                </label>
                <span className="font-mono" style={{ color: 'var(--accent-indigo)', fontWeight: 700 }}>
                  {maxRecovery} attempts
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                value={maxRecovery}
                onChange={(e) => setMaxRecovery(e.target.value)}
                style={{ width: '100%', accentColor: 'var(--accent-indigo)' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Prevents infinite loop retries for unrecoverable errors.</span>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Max Dynamic Task Replans
                </label>
                <span className="font-mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                  {maxReplan} replans
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="4"
                value={maxReplan}
                onChange={(e) => setMaxReplan(e.target.value)}
                style={{ width: '100%', accentColor: 'var(--accent-cyan)' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Bounds dynamic replanning cascades.</span>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Verification Confidence Threshold
                </label>
                <span className="font-mono" style={{ color: '#34d399', fontWeight: 700 }}>
                  {(confidenceThreshold * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0.40"
                max="0.95"
                step="0.05"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(e.target.value)}
                style={{ width: '100%', accentColor: '#10b981' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Outputs below this score trigger error diagnosis & recovery.</span>
            </div>
          </div>
        </div>

        {/* Security & Sandbox Allowlist Review */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: '#10b981' }}>
            <Shield size={20} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>Tool Sandbox Allowlist Policy</h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            Strict allowlist enforcement prevents arbitrary shell execution, unauthorized path traversal, or uninspected command injection:
          </p>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {settingsData?.allowed_tools?.map((tool) => (
              <span
                key={tool}
                className="font-mono"
                style={{
                  padding: '0.35rem 0.75rem',
                  borderRadius: '6px',
                  background: 'var(--bg-input)',
                  border: '1px solid var(--border-subtle)',
                  color: '#34d399',
                  fontSize: '0.8rem',
                }}
              >
                ✓ {tool}
              </span>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button
            type="submit"
            disabled={saving}
            className="btn btn-primary"
            style={{ padding: '0.75rem 2rem' }}
          >
            {saving ? (
              <>
                <RefreshCw size={16} className="spin-animate" />
                <span>Applying Settings...</span>
              </>
            ) : (
              <>
                <Save size={16} />
                <span>Save Runtime Settings</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
