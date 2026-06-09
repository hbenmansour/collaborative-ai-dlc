'use client';

import { useEffect, useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { api } from '@/lib/api-client';
import { Contract, ContractStatus, LeaseType, PaginatedResponse } from '@/lib/contracts';
import { Button } from '@/components/ui';
import { ContractStatusBadge } from '@/components/contracts/ContractStatusBadge';
import { ContractFilters } from '@/components/contracts/ContractFilters';

export default function ContractsPage() {
  const t = useTranslations('contracts');
  const router = useRouter();
  const pathname = usePathname();

  const [contracts, setContracts] = useState<Contract[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<ContractStatus | ''>('');
  const [leaseType, setLeaseType] = useState<LeaseType | ''>('');

  const pageSize = 20;

  const fetchContracts = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number | undefined> = {
        page,
        page_size: pageSize,
      };
      if (search) params.search = search;
      if (status) params.status = status;
      if (leaseType) params.lease_type = leaseType;

      const data = await api.get<PaginatedResponse<Contract>>('/api/v1/contracts', params);
      setContracts(data.items);
      setTotal(data.total);
    } catch {
      setContracts([]);
    } finally {
      setLoading(false);
    }
  }, [page, search, status, leaseType]);

  useEffect(() => {
    fetchContracts();
  }, [fetchContracts]);

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div data-testid="contracts-page" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700 }}>{t('title')}</h1>
        <Button
          onClick={() => router.push(`${pathname}/new`)}
          data-testid="new-contract-btn"
        >
          {t('newContract')}
        </Button>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <ContractFilters
          search={search}
          status={status}
          leaseType={leaseType}
          onSearchChange={(v) => { setSearch(v); setPage(1); }}
          onStatusChange={(v) => { setStatus(v); setPage(1); }}
          onLeaseTypeChange={(v) => { setLeaseType(v); setPage(1); }}
        />
      </div>

      {loading ? (
        <p>{t('loading')}</p>
      ) : (
        <>
          <div style={{ overflowX: 'auto', border: '1px solid var(--color-border)', borderRadius: '8px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }} data-testid="contracts-table">
              <thead>
                <tr style={{ background: '#f9fafb' }}>
                  <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600 }}>{t('contractNumber')}</th>
                  <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600 }}>{t('leaseType')}</th>
                  <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600 }}>{t('status')}</th>
                  <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600 }}>{t('startDate')}</th>
                  <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600 }}>{t('endDate')}</th>
                </tr>
              </thead>
              <tbody>
                {contracts.length === 0 ? (
                  <tr>
                    <td colSpan={5} style={{ textAlign: 'center', padding: '32px', color: '#6b7280' }}>
                      {t('noContracts')}
                    </td>
                  </tr>
                ) : (
                  contracts.map((c) => (
                    <tr
                      key={c.id}
                      onClick={() => router.push(`${pathname}/${c.id}`)}
                      style={{ cursor: 'pointer', borderBottom: '1px solid var(--color-border)' }}
                      data-testid={`contract-row-${c.id}`}
                    >
                      <td style={{ padding: '12px 16px' }}>{c.contract_number}</td>
                      <td style={{ padding: '12px 16px', textTransform: 'capitalize' }}>{c.lease_type}</td>
                      <td style={{ padding: '12px 16px' }}><ContractStatusBadge status={c.status} /></td>
                      <td style={{ padding: '12px 16px' }}>{c.start_date || '—'}</td>
                      <td style={{ padding: '12px 16px' }}>{c.end_date || '—'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '16px' }}>
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                data-testid="prev-page-btn"
              >
                {t('prev')}
              </Button>
              <span style={{ padding: '6px 12px', fontSize: '14px' }}>
                {page} / {totalPages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                data-testid="next-page-btn"
              >
                {t('nextPage')}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
