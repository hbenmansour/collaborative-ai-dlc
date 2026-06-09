export type ContractStatus = 'draft' | 'active' | 'suspended' | 'terminated' | 'expired';
export type LeaseType = 'vehicle' | 'equipment' | 'financial';
export type PaymentFrequency = 'monthly' | 'quarterly' | 'annually';

export interface ContractTerms {
  duration_months: number;
  payment_frequency: PaymentFrequency;
  interest_rate: number;
  residual_value: number;
  down_payment: number;
  monthly_payment: number;
}

export interface Contract {
  id: string;
  contract_number: string;
  type: LeaseType;
  status: ContractStatus;
  customer_name: string;
  start_date: string;
  end_date: string;
  terms: ContractTerms;
  country_code: string;
  currency: string;
}

export interface AmendmentRequest {
  contract_id: string;
  effective_date: string;
  reason: string;
  new_terms: Partial<ContractTerms>;
}

export interface RenewalRequest {
  contract_id: string;
  new_duration_months: number;
  new_interest_rate?: number;
  new_payment_frequency?: PaymentFrequency;
  new_residual_value?: number;
}

export interface TerminationPenalty {
  outstanding_principal: number;
  penalty_amount: number;
  deposit_held: number;
  settlement_total: number;
  formula_used: string;
}

export interface TerminationRequest {
  contract_id: string;
  termination_date: string;
  reason: string;
  end_of_lease_option: 'return_asset' | 'buyout';
}

export interface StatusTimelineEvent {
  status: ContractStatus;
  date: string;
  label: string;
  description?: string;
  active?: boolean;
}
