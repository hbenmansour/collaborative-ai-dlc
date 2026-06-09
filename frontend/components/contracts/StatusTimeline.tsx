'use client';

import { StatusTimelineEvent } from '@/lib/contract-lifecycle';

interface StatusTimelineProps {
  events: StatusTimelineEvent[];
}

export function StatusTimeline({ events }: StatusTimelineProps) {
  return (
    <>
      <div className="timeline" data-testid="status-timeline">
        {events.map((event, index) => (
          <div
            key={`${event.status}-${index}`}
            className={`timeline-item ${event.active ? 'active' : ''}`}
            data-testid={`timeline-event-${event.status}`}
          >
            <div className="timeline-marker" />
            <div className="timeline-content">
              <span className="timeline-date">{event.date}</span>
              <span className="timeline-label">{event.label}</span>
              {event.description && (
                <span className="timeline-desc">{event.description}</span>
              )}
            </div>
          </div>
        ))}
      </div>
      <style jsx>{`
        .timeline {
          display: flex;
          flex-direction: column;
          gap: 0;
          padding: 16px 0;
        }
        .timeline-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 12px 0;
          position: relative;
        }
        .timeline-item:not(:last-child)::after {
          content: '';
          position: absolute;
          left: 7px;
          top: 32px;
          bottom: -12px;
          width: 2px;
          background: var(--color-border, #e5e7eb);
        }
        .timeline-item.active .timeline-marker {
          background: var(--color-primary, #1a56db);
          box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.2);
        }
        .timeline-item.active::after {
          background: var(--color-primary, #1a56db);
        }
        .timeline-marker {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: var(--color-border, #e5e7eb);
          flex-shrink: 0;
          margin-top: 2px;
        }
        .timeline-content {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .timeline-date {
          font-size: 12px;
          color: #6b7280;
        }
        .timeline-label {
          font-size: 14px;
          font-weight: 500;
          color: var(--color-text, #111827);
        }
        .timeline-desc {
          font-size: 13px;
          color: #6b7280;
        }
      `}</style>
    </>
  );
}
