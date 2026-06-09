'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { ChatMessage as ChatMessageType, invokeAgentStream } from '@/lib/agent-client';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const t = useTranslations('chat');

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = useCallback(async (content: string) => {
    const userMsg: ChatMessageType = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    const assistantMsg: ChatMessageType = {
      id: `msg-${Date.now()}-assistant`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    abortRef.current = new AbortController();

    try {
      await invokeAgentStream(
        { message: content, sessionId },
        (chunk) => {
          if (chunk.type === 'text' && chunk.content) {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              updated[updated.length - 1] = { ...last, content: last.content + chunk.content };
              return updated;
            });
          } else if (chunk.type === 'structured_data' && chunk.data) {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              updated[updated.length - 1] = { ...last, structuredData: chunk.data };
              return updated;
            });
          } else if (chunk.type === 'done' && chunk.sessionId) {
            setSessionId(chunk.sessionId);
          }
        },
        abortRef.current.signal
      );
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          updated[updated.length - 1] = {
            ...last,
            content: t('error'),
          };
          return updated;
        });
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
    }
  }, [sessionId, t]);

  function handleNewChat() {
    if (abortRef.current) abortRef.current.abort();
    setMessages([]);
    setSessionId(undefined);
    setIsStreaming(false);
  }

  return (
    <div className="chat-panel" data-testid="chat-panel">
      <div className="chat-panel__header">
        <h2>{t('title')}</h2>
        <button
          onClick={handleNewChat}
          className="chat-panel__new-chat"
          data-testid="chat-new-session"
        >
          {t('newChat')}
        </button>
      </div>
      <div className="chat-panel__messages" data-testid="chat-messages">
        {messages.length === 0 && (
          <div className="chat-panel__empty" data-testid="chat-empty">
            <p>{t('emptyState')}</p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
