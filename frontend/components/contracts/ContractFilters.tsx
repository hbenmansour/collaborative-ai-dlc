'use client';

import { useTranslations } from 'next-intl';
import { ContractStatus, LeaseType } from '@/lib/contracts';

interface ContractFiltersProps {
  search: string;
  status: ContractStatus | '';
  leaseType: LeaseType | '';
  onSearchChange: (value: string) => void;
  onStatusChange: (value: ContractStatus | '') => void;
  onLeaseTypeChange: (value: LeaseType | '') => void;
}

export function ContractFilters({
  search,
  status,
  leaseType,
  onSearchChange,
  onStatusChange,
  onLeaseTypeChange,
}: ContractFiltersProps) {
  const t = useTranslations('contracts');

  return (
    <div data-testid="contract-filters" style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
      <input
        type="text"
        placeholder={t('searchPlaceholder')}
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        data-testid="contract-search-input"
        style={{
          padding: '8px 12px',
          border: '1px solid var(--color-border)',
          borderRadius: '6px',
          fontSize: '14px',
          flex: '1',
          minWidth: '200px',
        }}
      />
      <select
        value={status}
        onChange={(e) => onStatusChange(e.target.value as ContractStatus | '')}
        data-testid="contract-status-filter"
        style={{
          padding: '8px 12px',
          border: '1px solid var(--color-border)',
          borderRadius: '6px',
          fontSize: '14px',
        }}
      >
        <option value="">{t('allStatuses')}</option>
        <option value="draft">{t('statusDraft')}</option>
        <option value="active">{t('statusActive')}</option>
        <option value="suspended">{t('statusSuspended')}</option>
        <option value="terminated">{t('statusTerminated')}</option>
        <option value="expired">{t('statusExpired')}</option>
      </select>
      <select
        value={leaseType}
        onChange={(e) => onLeaseTypeChange(e.target.value as LeaseType | '')}
        data-testid="contract-type-filter"
        style={{
          padding: '8px 12px',
          border: '1px solid var(--color-border)',
          borderRadius: '6px',
          fontSize: '14px',
        }}
      >
        <option value="">{t('allTypes')}</option>
        <option value="vehicle">{t('typeVehicle')}</option>
        <option value="equipment">{t('typeEquipment')}</option>
        <option value="financial">{t('typeFinancial')}</option>
      </select>
    </div>
  );
}
