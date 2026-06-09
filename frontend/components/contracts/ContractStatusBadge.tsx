'use client';

import { ContractStatus } from '@/lib/contracts';

const statusStyles: Record<ContractStatus, { bg: string; color: string }> = {
  draft: { bg: '#f3f4f6', color: '#374151' },
  active: { bg: '#dcfce7', color: '#166534' },
  suspended: { bg: '#fef9c3', color: '#854d0e' },
  terminated: { bg: '#fee2e2', color: '#991b1b' },
  expired: { bg: '#e5e7eb', color: '#6b7280' },
};

export function ContractStatusBadge({ status }: { status: ContractStatus }) {
  const style = statusStyles[status] || statusStyles.draft;
  return (
    <span
      data-testid={`status-badge-${status}`}
      style={{
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 600,
        background: style.bg,
        color: style.color,
        textTransform: 'capitalize',
      }}
    >
      {status}
    </span>
  );
}
