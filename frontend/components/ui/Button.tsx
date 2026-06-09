'use client';

import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...props
}: ButtonProps) {
  return (
    <>
      <button
        className={`btn btn-${variant} btn-${size} ${className}`}
        data-testid={props['data-testid']}
        {...props}
      >
        {children}
      </button>
      <style jsx>{`
        .btn {
          border: none;
          border-radius: 6px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.15s, opacity 0.15s;
          display: inline-flex;
          align-items: center;
          gap: 6px;
        }
        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .btn-sm { padding: 6px 12px; font-size: 13px; }
        .btn-md { padding: 8px 16px; font-size: 14px; }
        .btn-lg { padding: 12px 24px; font-size: 16px; }
        .btn-primary {
          background: var(--color-primary);
          color: #fff;
        }
        .btn-primary:hover:not(:disabled) {
          background: var(--color-primary-hover);
        }
        .btn-secondary {
          background: #fff;
          color: var(--color-text);
          border: 1px solid var(--color-border);
        }
        .btn-secondary:hover:not(:disabled) {
          background: #f3f4f6;
        }
        .btn-danger {
          background: #dc2626;
          color: #fff;
        }
        .btn-danger:hover:not(:disabled) {
          background: #b91c1c;
        }
      `}</style>
    </>
  );
}
