import React from 'react';

export default function StatusBadge({ status }) {
  const norm = (status || 'PENDING').toUpperCase();

  let badgeClass = 'badge-pending';
  let label = norm;

  switch (norm) {
    case 'COMPLETED':
    case 'SUCCESS':
      badgeClass = 'badge-completed';
      label = 'Completed';
      break;
    case 'RECOVERED':
      badgeClass = 'badge-recovered';
      label = 'Self-Healed';
      break;
    case 'FAILED':
    case 'ABORTED':
      badgeClass = 'badge-failed';
      label = 'Failed';
      break;
    case 'RUNNING':
      badgeClass = 'badge-running';
      label = 'Running';
      break;
    case 'PENDING':
      badgeClass = 'badge-pending';
      label = 'Pending';
      break;
    case 'RETRY':
      badgeClass = 'badge-running';
      label = 'Retry';
      break;
    case 'CHANGE_ARGUMENTS':
      badgeClass = 'badge-recovered';
      label = 'Arg Adaptation';
      break;
    case 'REPLAN':
      badgeClass = 'badge-recovered';
      label = 'Dynamic Replan';
      break;
    case 'STOP':
      badgeClass = 'badge-failed';
      label = 'Halted (Safe)';
      break;
    default:
      badgeClass = 'badge-pending';
  }

  return (
    <span className={`badge ${badgeClass}`}>
      <span className="badge-dot" />
      {label}
    </span>
  );
}
