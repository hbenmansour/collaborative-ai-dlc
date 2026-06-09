'use client';

import { ReactNode } from 'react';

interface FormFieldProps {
  label: string;
  htmlFor?: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
}

export function FormField({ label, htmlFor, error, required, children }: FormFieldProps) {
  return (
    <>
      <div className="form-field" data-testid={`field-${htmlFor}`}>
        <label htmlFor={htmlFor} className="form-label">
          {label}
          {required && <span className="required">*</span>}
        </label>
        {children}
        {error && <span className="field-error">{error}</span>}
      </div>
      <style jsx>{`
        .form-field {
          display: flex;
          flex-direction: column;
          gap: 4px;
          margin-bottom: 16px;
        }
        .form-label {
          font-size: 14px;
          font-weight: 500;
          color: var(--color-text);
        }
        .required {
          color: #dc2626;
          margin-left: 2px;
        }
        .field-error {
          font-size: 12px;
          color: #dc2626;
        }
      `}</style>
    </>
  );
}
