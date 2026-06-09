export type LeaseType = 'vehicle' | 'equipment' | 'financial';
export type ContractStatus = 'draft' | 'active' | 'suspended' | 'terminated' | 'expired';
export type PaymentFrequency = 'monthly' | 'quarterly' | 'annually';

export interface ContractTerms {
  id: string;
  duration_months: number;
  payment_frequency: PaymentFrequency;
  interest_rate: number;
  residual_value: number;
  down_payment: number;
  currency_code: string;
}

export interface Contract {
  id: string;
  contract_number: string;
  lease_type: LeaseType;
  status: ContractStatus;
  customer_id: string;
  country_code: string;
  asset_description: string | null;
  asset_value: number | null;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
  terms: ContractTerms | null;
}

export interface ContractCreate {
  contract_number: string;
  lease_type: LeaseType;
  customer_id: string;
  country_code: string;
  asset_description?: string;
  asset_value?: number;
  start_date?: string;
  end_date?: string;
  terms?: Omit<ContractTerms, 'id'>;
}

export interface ContractListParams {
  page?: number;
  page_size?: number;
  status?: ContractStatus;
  lease_type?: LeaseType;
  search?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
