'use client';

import { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, id, ...props }: InputProps) {
  const inputId = id || props.name;
  return (
    <>
      <div className="input-wrapper">
        {label && (
          <label htmlFor={inputId} className="input-label">
            {label}
          </label>
        )}
        <input
          id={inputId}
          className={`input ${error ? 'input-error' : ''}`}
          data-testid={props['data-testid'] || `input-${inputId}`}
          {...props}
        />
        {error && <span className="error-text">{error}</span>}
      </div>
      <style jsx>{`
        .input-wrapper {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .input-label {
          font-size: 14px;
          font-weight: 500;
          color: var(--color-text);
        }
        .input {
          padding: 8px 12px;
          border: 1px solid var(--color-border);
          border-radius: 6px;
          font-size: 14px;
          outline: none;
          transition: border-color 0.15s;
        }
        .input:focus {
          border-color: var(--color-primary);
          box-shadow: 0 0 0 2px rgba(26, 86, 219, 0.1);
        }
        .input-error {
          border-color: #dc2626;
        }
        .error-text {
          font-size: 12px;
          color: #dc2626;
        }
      `}</style>
    </>
  );
}
