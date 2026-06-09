'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { FormField } from '@/components/ui/FormField';
import { api } from '@/lib/api-client';
import { Contract, RenewalRequest, PaymentFrequency } from '@/lib/contract-lifecycle';

type Step = 'terms' | 'review' | 'confirm';

export default function RenewContractPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [step, setStep] = useState<Step>('terms');
  const [loading, setLoading] = useState(false);
  const [contract, setContract] = useState<Contract | null>(null);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    new_duration_months: '',
    new_interest_rate: '',
    new_payment_frequency: '' as PaymentFrequency | '',
    new_residual_value: '',
  });

  // Load contract on mount
  useState(() => {
    api.get<Contract>(`/api/v1/contracts/${id}`).then((c) => {
      setContract(c);
      setForm({
        new_duration_months: String(c.terms.duration_months),
        new_interest_rate: String(c.terms.interest_rate),
        new_payment_frequency: c.terms.payment_frequency,
        new_residual_value: String(c.terms.residual_value),
      });
    }).catch(() => setError('Failed to load contract'));
  });

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!contract) return;
    setLoading(true);
    setError('');

    const payload: RenewalRequest = {
      contract_id: id,
      new_duration_months: Number(form.new_duration_months),
      ...(form.new_interest_rate && { new_interest_rate: Number(form.new_interest_rate) }),
      ...(form.new_payment_frequency && { new_payment_frequency: form.new_payment_frequency as PaymentFrequency }),
      ...(form.new_residual_value && { new_residual_value: Number(form.new_residual_value) }),
    };

    try {
      await api.post(`/api/v1/contracts/${id}/renew`, payload);
      router.push(`../`);
    } catch {
      setError('Failed to submit renewal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="page" data-testid="renew-contract-page">
        <h1>Renew Contract</h1>
        {error && <p className="error">{error}</p>}

        <div className="wizard-steps">
          <span className={step === 'terms' ? 'active' : ''}>1. Terms</span>
          <span className={step === 'review' ? 'active' : ''}>2. Review</span>
          <span className={step === 'confirm' ? 'active' : ''}>3. Confirm</span>
        </div>

        {contract && step === 'terms' && (
          <div className="step-content" data-testid="step-terms">
            <p className="hint">Pre-populated from original contract. Modify as needed.</p>
            <FormField label="Duration (months)" htmlFor="new_duration_months" required>
              <Input
                type="number"
                name="new_duration_months"
                value={form.new_duration_months}
                onChange={(e) => handleChange('new_duration_months', e.target.value)}
                required
                data-testid="input-renewal-duration"
              />
            </FormField>
            <FormField label="Interest Rate (%)" htmlFor="new_interest_rate">
              <Input
                type="number"
                step="0.01"
                name="new_interest_rate"
                value={form.new_interest_rate}
                onChange={(e) => handleChange('new_interest_rate', e.target.value)}
                data-testid="input-renewal-rate"
              />
            </FormField>
            <FormField label="Payment Frequency" htmlFor="new_payment_frequency">
              <select
                id="new_payment_frequency"
                value={form.new_payment_frequency}
                onChange={(e) => handleChange('new_payment_frequency', e.target.value)}
                className="select"
                data-testid="select-renewal-frequency"
              >
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="annually">Annually</option>
              </select>
            </FormField>
            <FormField label="Residual Value" htmlFor="new_residual_value">
              <Input
                type="number"
                step="0.01"
                name="new_residual_value"
                value={form.new_residual_value}
                onChange={(e) => handleChange('new_residual_value', e.target.value)}
                data-testid="input-renewal-residual"
              />
            </FormField>
            <div className="actions">
              <Button variant="secondary" type="button" onClick={() => router.back()} data-testid="btn-cancel">
                Cancel
              </Button>
              <Button type="button" onClick={() => setStep('review')} data-testid="btn-next">
                Next: Review
              </Button>
            </div>
          </div>
        )}

        {contract && step === 'review' && (
          <div className="step-content" data-testid="step-review">
            <h3>Renewal Summary</h3>
            <dl className="summary">
              <dt>Contract</dt><dd>{contract.contract_number}</dd>
              <dt>New Duration</dt><dd>{form.new_duration_months} months</dd>
              <dt>Interest Rate</dt><dd>{form.new_interest_rate}%</dd>
              <dt>Payment Frequency</dt><dd>{form.new_payment_frequency}</dd>
              <dt>Residual Value</dt><dd>{contract.currency} {form.new_residual_value}</dd>
            </dl>
            <div className="actions">
              <Button variant="secondary" type="button" onClick={() => setStep('terms')} data-testid="btn-back">
                Back
              </Button>
              <Button type="button" onClick={() => setStep('confirm')} data-testid="btn-next-confirm">
                Next: Confirm
              </Button>
            </div>
          </div>
        )}

        {contract && step === 'confirm' && (
          <div className="step-content" data-testid="step-confirm">
            <p>A new payment schedule will be generated for the renewal period. The original contract will be linked.</p>
            <div className="actions">
              <Button variant="secondary" type="button" onClick={() => setStep('review')} data-testid="btn-back">
                Back
              </Button>
              <Button type="button" onClick={handleSubmit} disabled={loading} data-testid="btn-submit-renewal">
                {loading ? 'Processing...' : 'Confirm Renewal'}
              </Button>
            </div>
          </div>
        )}
      </div>
      <style jsx>{`
        .page { padding: 24px; max-width: 640px; }
        .error { color: #dc2626; margin-bottom: 16px; }
        .wizard-steps { display: flex; gap: 24px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--color-border, #e5e7eb); }
        .wizard-steps span { font-size: 14px; color: #6b7280; }
        .wizard-steps span.active { color: var(--color-primary, #1a56db); font-weight: 600; }
        .step-content { background: #f9fafb; border: 1px solid var(--color-border, #e5e7eb); border-radius: 8px; padding: 20px; }
        .hint { font-size: 13px; color: #6b7280; margin-bottom: 16px; }
        .select { padding: 8px 12px; border: 1px solid var(--color-border, #e5e7eb); border-radius: 6px; font-size: 14px; width: 100%; }
        h3 { margin: 0 0 12px; font-size: 16px; }
        .summary { display: grid; grid-template-columns: auto 1fr; gap: 8px 16px; margin-bottom: 20px; }
        dt { font-weight: 500; font-size: 14px; color: #6b7280; }
        dd { margin: 0; font-size: 14px; }
        .actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }
      `}</style>
    </>
  );
}
