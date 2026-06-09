'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { api } from '@/lib/api-client';
import { ContractCreate, LeaseType, PaymentFrequency } from '@/lib/contracts';
import { Button, Input, FormField } from '@/components/ui';

type Step = 'basics' | 'asset' | 'terms' | 'review';
const STEPS: Step[] = ['basics', 'asset', 'terms', 'review'];

export default function NewContractPage() {
  const t = useTranslations('contracts');
  const router = useRouter();
  const pathname = usePathname();
  const locale = pathname.split('/')[1] || 'en';

  const [step, setStep] = useState<Step>('basics');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState<ContractCreate>({
    contract_number: '',
    lease_type: 'vehicle',
    customer_id: '',
    country_code: '',
    asset_description: '',
    asset_value: undefined,
    start_date: '',
    end_date: '',
    terms: {
      duration_months: 12,
      payment_frequency: 'monthly',
      interest_rate: 0,
      residual_value: 0,
      down_payment: 0,
      currency_code: '',
    },
  });

  const stepIndex = STEPS.indexOf(step);

  const goNext = () => setStep(STEPS[stepIndex + 1]);
  const goPrev = () => setStep(STEPS[stepIndex - 1]);

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');
    try {
      await api.post('/api/v1/contracts', form);
      router.push(`/${locale}/contracts`);
    } catch {
      setError(t('createError'));
    } finally {
      setSubmitting(false);
    }
  };

  const updateField = (field: string, value: unknown) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const updateTerms = (field: string, value: unknown) => {
    setForm((prev) => ({
      ...prev,
      terms: { ...prev.terms!, [field]: value },
    }));
  };

  return (
    <div data-testid="new-contract-page" style={{ padding: '24px', maxWidth: '700px' }}>
      <h1 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '8px' }}>{t('newContract')}</h1>

      {/* Step indicator */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '32px' }}>
        {STEPS.map((s, i) => (
          <div
            key={s}
            data-testid={`step-indicator-${s}`}
            style={{
              flex: 1,
              height: '4px',
              borderRadius: '2px',
              background: i <= stepIndex ? 'var(--color-primary)' : '#e5e7eb',
            }}
          />
        ))}
      </div>

      {/* Step: Basics */}
      {step === 'basics' && (
        <div data-testid="step-basics">
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>{t('stepBasics')}</h2>
          <FormField label={t('contractNumber')} htmlFor="contract_number" required>
            <Input
              name="contract_number"
              value={form.contract_number}
              onChange={(e) => updateField('contract_number', e.target.value)}
              required
            />
          </FormField>
          <FormField label={t('leaseType')} htmlFor="lease_type" required>
            <select
              id="lease_type"
              value={form.lease_type}
              onChange={(e) => updateField('lease_type', e.target.value as LeaseType)}
              data-testid="input-lease_type"
              style={{ padding: '8px 12px', border: '1px solid var(--color-border)', borderRadius: '6px', fontSize: '14px' }}
            >
              <option value="vehicle">{t('typeVehicle')}</option>
              <option value="equipment">{t('typeEquipment')}</option>
              <option value="financial">{t('typeFinancial')}</option>
            </select>
          </FormField>
          <FormField label={t('customer')} htmlFor="customer_id" required>
            <Input
              name="customer_id"
              value={form.customer_id}
              onChange={(e) => updateField('customer_id', e.target.value)}
              placeholder={t('customerIdPlaceholder')}
              required
            />
          </FormField>
          <FormField label={t('countryCode')} htmlFor="country_code" required>
            <Input
              name="country_code"
              value={form.country_code}
              onChange={(e) => updateField('country_code', e.target.value)}
              placeholder="e.g. FRA"
              required
            />
          </FormField>
        </div>
      )}

      {/* Step: Asset */}
      {step === 'asset' && (
        <div data-testid="step-asset">
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>{t('stepAsset')}</h2>
          <FormField label={t('assetDescription')} htmlFor="asset_description">
            <Input
              name="asset_description"
              value={form.asset_description || ''}
              onChange={(e) => updateField('asset_description', e.target.value)}
            />
          </FormField>
          <FormField label={t('assetValue')} htmlFor="asset_value">
            <Input
              name="asset_value"
              type="number"
              value={form.asset_value ?? ''}
              onChange={(e) => updateField('asset_value', e.target.value ? Number(e.target.value) : undefined)}
            />
          </FormField>
          <FormField label={t('startDate')} htmlFor="start_date">
            <Input
              name="start_date"
              type="date"
              value={form.start_date || ''}
              onChange={(e) => updateField('start_date', e.target.value)}
            />
          </FormField>
          <FormField label={t('endDate')} htmlFor="end_date">
            <Input
              name="end_date"
              type="date"
              value={form.end_date || ''}
              onChange={(e) => updateField('end_date', e.target.value)}
            />
          </FormField>
        </div>
      )}

      {/* Step: Terms */}
      {step === 'terms' && (
        <div data-testid="step-terms">
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>{t('stepTerms')}</h2>
          <FormField label={t('durationMonths')} htmlFor="duration_months" required>
            <Input
              name="duration_months"
              type="number"
              value={form.terms?.duration_months ?? ''}
              onChange={(e) => updateTerms('duration_months', Number(e.target.value))}
              required
            />
          </FormField>
          <FormField label={t('paymentFrequency')} htmlFor="payment_frequency">
            <select
              id="payment_frequency"
              value={form.terms?.payment_frequency || 'monthly'}
              onChange={(e) => updateTerms('payment_frequency', e.target.value as PaymentFrequency)}
              data-testid="input-payment_frequency"
              style={{ padding: '8px 12px', border: '1px solid var(--color-border)', borderRadius: '6px', fontSize: '14px' }}
            >
              <option value="monthly">{t('freqMonthly')}</option>
              <option value="quarterly">{t('freqQuarterly')}</option>
              <option value="annually">{t('freqAnnually')}</option>
            </select>
          </FormField>
          <FormField label={t('interestRate')} htmlFor="interest_rate" required>
            <Input
              name="interest_rate"
              type="number"
              step="0.001"
              value={form.terms?.interest_rate ?? ''}
              onChange={(e) => updateTerms('interest_rate', Number(e.target.value))}
              required
            />
          </FormField>
          <FormField label={t('residualValue')} htmlFor="residual_value">
            <Input
              name="residual_value"
              type="number"
              value={form.terms?.residual_value ?? ''}
              onChange={(e) => updateTerms('residual_value', Number(e.target.value))}
            />
          </FormField>
          <FormField label={t('downPayment')} htmlFor="down_payment">
            <Input
              name="down_payment"
              type="number"
              value={form.terms?.down_payment ?? ''}
              onChange={(e) => updateTerms('down_payment', Number(e.target.value))}
            />
          </FormField>
          <FormField label={t('currencyCode')} htmlFor="currency_code" required>
            <Input
              name="currency_code"
              value={form.terms?.currency_code || ''}
              onChange={(e) => updateTerms('currency_code', e.target.value)}
              placeholder="e.g. EUR"
              required
            />
          </FormField>
        </div>
      )}

      {/* Step: Review */}
      {step === 'review' && (
        <div data-testid="step-review">
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>{t('stepReview')}</h2>
          <dl style={{ fontSize: '14px', lineHeight: 1.8 }}>
            <dt style={{ fontWeight: 600 }}>{t('contractNumber')}</dt>
            <dd style={{ marginBottom: '8px' }}>{form.contract_number}</dd>
            <dt style={{ fontWeight: 600 }}>{t('leaseType')}</dt>
            <dd style={{ marginBottom: '8px', textTransform: 'capitalize' }}>{form.lease_type}</dd>
            <dt style={{ fontWeight: 600 }}>{t('assetDescription')}</dt>
            <dd style={{ marginBottom: '8px' }}>{form.asset_description || '—'}</dd>
            <dt style={{ fontWeight: 600 }}>{t('assetValue')}</dt>
            <dd style={{ marginBottom: '8px' }}>{form.asset_value ?? '—'}</dd>
            <dt style={{ fontWeight: 600 }}>{t('durationMonths')}</dt>
            <dd style={{ marginBottom: '8px' }}>{form.terms?.duration_months}</dd>
            <dt style={{ fontWeight: 600 }}>{t('interestRate')}</dt>
            <dd style={{ marginBottom: '8px' }}>{form.terms?.interest_rate}%</dd>
          </dl>
          {error && <p style={{ color: '#dc2626', marginTop: '8px' }}>{error}</p>}
        </div>
      )}

      {/* Navigation buttons */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
        <Button
          variant="secondary"
          onClick={stepIndex === 0 ? () => router.push(`/${locale}/contracts`) : goPrev}
          data-testid="wizard-back-btn"
        >
          {stepIndex === 0 ? t('cancelBtn') : t('prevStep')}
        </Button>
        {step === 'review' ? (
          <Button
            onClick={handleSubmit}
            disabled={submitting}
            data-testid="wizard-submit-btn"
          >
            {submitting ? t('submitting') : t('createContract')}
          </Button>
        ) : (
          <Button onClick={goNext} data-testid="wizard-next-btn">
            {t('nextStep')}
          </Button>
        )}
      </div>
    </div>
  );
}
