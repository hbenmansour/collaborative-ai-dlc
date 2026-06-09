'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui';

interface ActivationChecklistProps {
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
}

const CHECKLIST_ITEMS = [
  'documentsVerified',
  'customerApproved',
  'creditCheckPassed',
  'termsConfirmed',
  'signaturesCollected',
] as const;

export function ActivationChecklist({ onConfirm, onCancel, loading }: ActivationChecklistProps) {
  const t = useTranslations('contracts.activation');
  const [checks, setChecks] = useState<Record<string, boolean>>({});

  const allChecked = CHECKLIST_ITEMS.every((item) => checks[item]);

  const toggle = (item: string) => {
    setChecks((prev) => ({ ...prev, [item]: !prev[item] }));
  };

  return (
    <div
      data-testid="activation-checklist"
      style={{
        border: '1px solid var(--color-border)',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px',
        background: '#f9fafb',
      }}
    >
      <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px' }}>
        {t('title')}
      </h3>
      <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px' }}>
        {t('description')}
      </p>
      <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 20px' }}>
        {CHECKLIST_ITEMS.map((item) => (
          <li key={item} style={{ marginBottom: '8px' }}>
            <label
              style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', cursor: 'pointer' }}
            >
              <input
                type="checkbox"
                checked={!!checks[item]}
                onChange={() => toggle(item)}
                data-testid={`checklist-${item}`}
              />
              {t(item)}
            </label>
          </li>
        ))}
      </ul>
      <div style={{ display: 'flex', gap: '8px' }}>
        <Button
          onClick={onConfirm}
          disabled={!allChecked || loading}
          data-testid="confirm-activation-btn"
        >
          {loading ? t('activating') : t('confirmActivation')}
        </Button>
        <Button variant="secondary" onClick={onCancel} data-testid="cancel-activation-btn">
          {t('cancel')}
        </Button>
      </div>
    </div>
  );
}
