'use client';

import { ChatMessage as ChatMessageType } from '@/lib/agent-client';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`chat-message ${isUser ? 'chat-message--user' : 'chat-message--assistant'}`}
      data-testid={`chat-message-${message.id}`}
    >
      <div className="chat-message__avatar" data-testid="chat-message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="chat-message__body">
        <div className="chat-message__content" data-testid="chat-message-content">
          {message.content}
        </div>
        {message.structuredData && (
          <StructuredDataCard data={message.structuredData} />
        )}
        <time className="chat-message__time" data-testid="chat-message-time">
          {message.timestamp.toLocaleTimeString()}
        </time>
      </div>
    </div>
  );
}

function StructuredDataCard({ data }: { data: Record<string, unknown> }) {
  // Render structured data (e.g. contract summaries) as a card
  const title = (data.title as string) || (data.contract_number as string) || 'Details';
  const entries = Object.entries(data).filter(([k]) => k !== 'title');

  return (
    <div className="chat-structured-card" data-testid="chat-structured-card">
      <div className="chat-structured-card__title">{title}</div>
      <dl className="chat-structured-card__list">
        {entries.map(([key, value]) => (
          <div key={key} className="chat-structured-card__item">
            <dt>{key.replace(/_/g, ' ')}</dt>
            <dd>{String(value)}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
