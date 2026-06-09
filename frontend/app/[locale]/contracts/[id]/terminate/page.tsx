'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { FormField } from '@/components/ui/FormField';
import { api } from '@/lib/api-client';
import { Contract, TerminationPenalty, TerminationRequest } from '@/lib/contract-lifecycle';

export default function TerminateContractPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [contract, setContract] = useState<Contract | null>(null);
  const [penalty, setPenalty] = useState<TerminationPenalty | null>(null);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    termination_date: '',
    reason: '',
    end_of_lease_option: 'return_asset' as 'return_asset' | 'buyout',
  });

  // Load contract on mount
  useState(() => {
    api.get<Contract>(`/api/v1/contracts/${id}`).then(setContract).catch(() => setError('Failed to load contract'));
  });

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handlePreviewPenalty = async () => {
    if (!form.termination_date) return;
    setLoading(true);
    try {
      const result = await api.post<TerminationPenalty>(`/api/v1/contracts/${id}/terminate/preview`, {
        termination_date: form.termination_date,
      });
      setPenalty(result);
    } catch {
      setError('Failed to calculate penalty');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const payload: TerminationRequest = {
      contract_id: id,
      termination_date: form.termination_date,
      reason: form.reason,
      end_of_lease_option: form.end_of_lease_option,
    };

    try {
      await api.post(`/api/v1/contracts/${id}/terminate`, payload);
      router.push(`../`);
    } catch {
      setError('Failed to process termination');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="page" data-testid="terminate-contract-page">
        <h1>Early Termination</h1>
        {error && <p className="error">{error}</p>}

        {contract && (
          <form onSubmit={handleSubmit} data-testid="termination-form">
            <div className="form-section">
              <FormField label="Termination Date" htmlFor="termination_date" required>
                <Input
                  type="date"
                  name="termination_date"
                  value={form.termination_date}
                  onChange={(e) => handleChange('termination_date', e.target.value)}
                  required
                  data-testid="input-termination-date"
                />
              </FormField>
              <FormField label="Reason" htmlFor="reason" required>
                <Input
                  name="reason"
                  value={form.reason}
                  onChange={(e) => handleChange('reason', e.target.value)}
                  placeholder="Reason for early termination"
                  required
                  data-testid="input-termination-reason"
                />
              </FormField>
              <FormField label="End of Lease Option" htmlFor="end_of_lease_option">
                <select
                  id="end_of_lease_option"
                  value={form.end_of_lease_option}
                  onChange={(e) => handleChange('end_of_lease_option', e.target.value)}
                  className="select"
                  data-testid="select-end-option"
                >
                  <option value="return_asset">Return Asset</option>
                  <option value="buyout">Buyout</option>
                </select>
              </FormField>

              <Button
                type="button"
                variant="secondary"
                onClick={handlePreviewPenalty}
                disabled={!form.termination_date || loading}
                data-testid="btn-preview-penalty"
              >
                Preview Penalty
              </Button>
            </div>

            {penalty && (
              <div className="penalty-preview" data-testid="penalty-preview">
                <h3>Settlement Calculation</h3>
                <dl className="settlement">
                  <dt>Outstanding Principal</dt>
                  <dd>{contract.currency} {penalty.outstanding_principal.toLocaleString()}</dd>
                  <dt>Penalty Amount</dt>
                  <dd className="penalty-amount">{contract.currency} {penalty.penalty_amount.toLocaleString()}</dd>
                  <dt>Deposit Held</dt>
                  <dd className="deposit">- {contract.currency} {penalty.deposit_held.toLocaleString()}</dd>
                  <dt className="total-label">Settlement Total</dt>
                  <dd className="total-value">{contract.currency} {penalty.settlement_total.toLocaleString()}</dd>
                </dl>
                <p className="formula">Formula: {penalty.formula_used}</p>
              </div>
            )}

            <div className="actions">
              <Button variant="secondary" type="button" onClick={() => router.back()} data-testid="btn-cancel">
                Cancel
              </Button>
              <Button variant="danger" type="submit" disabled={loading || !penalty} data-testid="btn-submit-termination">
                {loading ? 'Processing...' : 'Confirm Termination'}
              </Button>
            </div>
          </form>
        )}
      </div>
      <style jsx>{`
        .page { padding: 24px; max-width: 640px; }
        .error { color: #dc2626; margin-bottom: 16px; }
        .form-section { background: #f9fafb; border: 1px solid var(--color-border, #e5e7eb); border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .select { padding: 8px 12px; border: 1px solid var(--color-border, #e5e7eb); border-radius: 6px; font-size: 14px; width: 100%; }
        .penalty-preview { background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        h3 { margin: 0 0 12px; font-size: 16px; }
        .settlement { display: grid; grid-template-columns: auto 1fr; gap: 8px 16px; }
        dt { font-size: 14px; color: #6b7280; }
        dd { margin: 0; font-size: 14px; text-align: right; }
        .penalty-amount { color: #dc2626; font-weight: 500; }
        .deposit { color: #059669; }
        .total-label { font-weight: 700; color: #111827; border-top: 1px solid #fecaca; padding-top: 8px; }
        .total-value { font-weight: 700; font-size: 16px; color: #111827; border-top: 1px solid #fecaca; padding-top: 8px; text-align: right; }
        .formula { font-size: 12px; color: #6b7280; margin-top: 12px; font-style: italic; }
        .actions { display: flex; gap: 12px; justify-content: flex-end; }
      `}</style>
    </>
  );
}
