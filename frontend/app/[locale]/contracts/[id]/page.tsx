'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter, usePathname } from 'next/navigation';
import { api } from '@/lib/api-client';
import { Contract } from '@/lib/contracts';
import { Button } from '@/components/ui';
import { ContractStatusBadge } from '@/components/contracts/ContractStatusBadge';
import { ActivationChecklist } from '@/components/contracts/ActivationChecklist';

export default function ContractDetailPage() {
  const t = useTranslations('contracts');
  const params = useParams();
  const router = useRouter();
  const pathname = usePathname();
  const locale = pathname.split('/')[1] || 'en';

  const [contract, setContract] = useState<Contract | null>(null);
  const [loading, setLoading] = useState(true);
  const [activating, setActivating] = useState(false);
  const [showChecklist, setShowChecklist] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get<Contract>(`/api/v1/contracts/${params.id}`);
        setContract(data);
      } catch {
        setContract(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [params.id]);

  const handleActivate = async () => {
    setActivating(true);
    try {
      await api.post(`/api/v1/contracts/${params.id}/activate`);
      const updated = await api.get<Contract>(`/api/v1/contracts/${params.id}`);
      setContract(updated);
      setShowChecklist(false);
    } catch {
      // error handled silently
    } finally {
      setActivating(false);
    }
  };

  if (loading) return <p style={{ padding: '24px' }}>{t('loading')}</p>;
  if (!contract) return <p style={{ padding: '24px' }}>{t('notFound')}</p>;

  return (
    <div data-testid="contract-detail-page" style={{ padding: '24px', maxWidth: '800px' }}>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => router.push(`/${locale}/contracts`)}
        data-testid="back-to-list-btn"
        style={{ marginBottom: '16px' }}
      >
        ← {t('backToList')}
      </Button>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700 }}>{contract.contract_number}</h1>
          <ContractStatusBadge status={contract.status} />
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {contract.status === 'draft' && (
            <Button
              onClick={() => setShowChecklist(true)}
              data-testid="activate-btn"
            >
              {t('activate')}
            </Button>
          )}
          {contract.status === 'active' && (
            <>
              <Button
                variant="secondary"
                onClick={() => router.push(`${pathname}/amend`)}
                data-testid="amend-btn"
              >
                {t('amend')}
              </Button>
              <Button
                variant="secondary"
                onClick={() => router.push(`${pathname}/renew`)}
                data-testid="renew-btn"
              >
                {t('renew')}
              </Button>
              <Button
                variant="danger"
                onClick={() => router.push(`${pathname}/terminate`)}
                data-testid="terminate-btn"
              >
                {t('terminate')}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Activation checklist modal */}
      {showChecklist && (
        <ActivationChecklist
          onConfirm={handleActivate}
          onCancel={() => setShowChecklist(false)}
          loading={activating}
        />
      )}

      {/* Contract details */}
      <section style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '12px' }}>{t('details')}</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '14px' }}>
          <div>
            <span style={{ fontWeight: 600 }}>{t('leaseType')}: </span>
            <span style={{ textTransform: 'capitalize' }}>{contract.lease_type}</span>
          </div>
          <div>
            <span style={{ fontWeight: 600 }}>{t('countryCode')}: </span>
            <span>{contract.country_code}</span>
          </div>
          <div>
            <span style={{ fontWeight: 600 }}>{t('startDate')}: </span>
            <span>{contract.start_date || '—'}</span>
          </div>
          <div>
            <span style={{ fontWeight: 600 }}>{t('endDate')}: </span>
            <span>{contract.end_date || '—'}</span>
          </div>
          <div>
            <span style={{ fontWeight: 600 }}>{t('assetDescription')}: </span>
            <span>{contract.asset_description || '—'}</span>
          </div>
          <div>
            <span style={{ fontWeight: 600 }}>{t('assetValue')}: </span>
            <span>{contract.asset_value ?? '—'}</span>
          </div>
        </div>
      </section>

      {/* Terms section */}
      {contract.terms && (
        <section>
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '12px' }}>{t('termsTitle')}</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '14px' }}>
            <div>
              <span style={{ fontWeight: 600 }}>{t('durationMonths')}: </span>
              <span>{contract.terms.duration_months}</span>
            </div>
            <div>
              <span style={{ fontWeight: 600 }}>{t('paymentFrequency')}: </span>
              <span style={{ textTransform: 'capitalize' }}>{contract.terms.payment_frequency}</span>
            </div>
            <div>
              <span style={{ fontWeight: 600 }}>{t('interestRate')}: </span>
              <span>{contract.terms.interest_rate}%</span>
            </div>
            <div>
              <span style={{ fontWeight: 600 }}>{t('residualValue')}: </span>
              <span>{contract.terms.residual_value}</span>
            </div>
            <div>
              <span style={{ fontWeight: 600 }}>{t('downPayment')}: </span>
              <span>{contract.terms.down_payment}</span>
            </div>
            <div>
              <span style={{ fontWeight: 600 }}>{t('currencyCode')}: </span>
              <span>{contract.terms.currency_code}</span>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
