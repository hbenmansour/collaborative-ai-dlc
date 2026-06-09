'use client';

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
}

export function Table<T extends Record<string, unknown>>({
  columns,
  data,
  onRowClick,
  emptyMessage = 'No data',
}: TableProps<T>) {
  return (
    <>
      <div className="table-wrapper" data-testid="data-table">
        <table className="table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key}>{col.header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="empty">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, i) => (
                <tr
                  key={i}
                  onClick={() => onRowClick?.(row)}
                  className={onRowClick ? 'clickable' : ''}
                >
                  {columns.map((col) => (
                    <td key={col.key}>
                      {col.render ? col.render(row) : String(row[col.key] ?? '')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <style jsx>{`
        .table-wrapper {
          overflow-x: auto;
          border: 1px solid var(--color-border);
          border-radius: 8px;
        }
        .table {
          width: 100%;
          border-collapse: collapse;
          font-size: 14px;
        }
        th {
          text-align: left;
          padding: 12px 16px;
          background: #f9fafb;
          font-weight: 600;
          border-bottom: 1px solid var(--color-border);
        }
        td {
          padding: 12px 16px;
          border-bottom: 1px solid var(--color-border);
        }
        tr:last-child td {
          border-bottom: none;
        }
        .clickable {
          cursor: pointer;
        }
        .clickable:hover {
          background: #f3f4f6;
        }
        .empty {
          text-align: center;
          color: var(--color-text-secondary);
          padding: 32px 16px;
        }
      `}</style>
    </>
  );
}
