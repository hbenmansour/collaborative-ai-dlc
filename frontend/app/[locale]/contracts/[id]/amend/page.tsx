'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { FormField } from '@/components/ui/FormField';
import { api } from '@/lib/api-client';
import { AmendmentRequest, Contract, ContractTerms } from '@/lib/contract-lifecycle';

export default function AmendContractPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [contract, setContract] = useState<Contract | null>(null);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    effective_date: '',
    reason: '',
    duration_months: '',
    interest_rate: '',
    monthly_payment: '',
    residual_value: '',
  });

  // Load contract on mount
  useState(() => {
    api.get<Contract>(`/api/v1/contracts/${id}`).then(setContract).catch(() => setError('Failed to load contract'));
  });

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!contract) return;
    setLoading(true);
    setError('');

    const new_terms: Partial<ContractTerms> = {};
    if (form.duration_months) new_terms.duration_months = Number(form.duration_months);
    if (form.interest_rate) new_terms.interest_rate = Number(form.interest_rate);
    if (form.monthly_payment) new_terms.monthly_payment = Number(form.monthly_payment);
    if (form.residual_value) new_terms.residual_value = Number(form.residual_value);

    const payload: AmendmentRequest = {
      contract_id: id,
      effective_date: form.effective_date,
      reason: form.reason,
      new_terms,
    };

    try {
      await api.post(`/api/v1/contracts/${id}/amend`, payload);
      router.push(`../`);
    } catch {
      setError('Failed to submit amendment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="page" data-testid="amend-contract-page">
        <h1>Amend Contract</h1>
        {error && <p className="error">{error}</p>}

        {contract && (
          <div className="comparison">
            <div className="terms-panel">
              <h3>Original Terms</h3>
              <dl>
                <dt>Duration</dt><dd>{contract.terms.duration_months} months</dd>
                <dt>Interest Rate</dt><dd>{contract.terms.interest_rate}%</dd>
                <dt>Monthly Payment</dt><dd>{contract.currency} {contract.terms.monthly_payment}</dd>
                <dt>Residual Value</dt><dd>{contract.currency} {contract.terms.residual_value}</dd>
              </dl>
            </div>

            <div className="terms-panel new-terms">
              <h3>New Terms</h3>
              <form onSubmit={handleSubmit} data-testid="amendment-form">
                <FormField label="Effective Date" htmlFor="effective_date" required>
                  <Input
                    type="date"
                    name="effective_date"
                    value={form.effective_date}
                    onChange={(e) => handleChange('effective_date', e.target.value)}
                    required
                    data-testid="input-effective-date"
                  />
                </FormField>
                <FormField label="Reason" htmlFor="reason" required>
                  <Input
                    name="reason"
                    value={form.reason}
                    onChange={(e) => handleChange('reason', e.target.value)}
                    placeholder="Reason for amendment"
                    required
                    data-testid="input-reason"
                  />
                </FormField>
                <FormField label="Duration (months)" htmlFor="duration_months">
                  <Input
                    type="number"
                    name="duration_months"
                    value={form.duration_months}
                    onChange={(e) => handleChange('duration_months', e.target.value)}
                    placeholder={String(contract.terms.duration_months)}
                    data-testid="input-duration"
                  />
                </FormField>
                <FormField label="Interest Rate (%)" htmlFor="interest_rate">
                  <Input
                    type="number"
                    step="0.01"
                    name="interest_rate"
                    value={form.interest_rate}
                    onChange={(e) => handleChange('interest_rate', e.target.value)}
                    placeholder={String(contract.terms.interest_rate)}
                    data-testid="input-interest-rate"
                  />
                </FormField>
                <FormField label="Monthly Payment" htmlFor="monthly_payment">
                  <Input
                    type="number"
                    step="0.01"
                    name="monthly_payment"
                    value={form.monthly_payment}
                    onChange={(e) => handleChange('monthly_payment', e.target.value)}
                    placeholder={String(contract.terms.monthly_payment)}
                    data-testid="input-monthly-payment"
                  />
                </FormField>
                <FormField label="Residual Value" htmlFor="residual_value">
                  <Input
                    type="number"
                    step="0.01"
                    name="residual_value"
                    value={form.residual_value}
                    onChange={(e) => handleChange('residual_value', e.target.value)}
                    placeholder={String(contract.terms.residual_value)}
                    data-testid="input-residual-value"
                  />
                </FormField>
                <div className="actions">
                  <Button variant="secondary" type="button" onClick={() => router.back()} data-testid="btn-cancel">
                    Cancel
                  </Button>
                  <Button type="submit" disabled={loading} data-testid="btn-submit-amendment">
                    {loading ? 'Submitting...' : 'Submit Amendment'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
      <style jsx>{`
        .page { padding: 24px; max-width: 960px; }
        .error { color: #dc2626; margin-bottom: 16px; }
        .comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        .terms-panel { background: #f9fafb; border: 1px solid var(--color-border, #e5e7eb); border-radius: 8px; padding: 20px; }
        .new-terms { background: #fff; }
        h3 { margin: 0 0 16px; font-size: 16px; }
        dl { display: grid; grid-template-columns: auto 1fr; gap: 8px 16px; }
        dt { font-weight: 500; font-size: 14px; color: #6b7280; }
        dd { margin: 0; font-size: 14px; }
        .actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }
      `}</style>
    </>
  );
}
