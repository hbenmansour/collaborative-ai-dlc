import { getAccessToken } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  structuredData?: Record<string, unknown>;
}

export interface AgentSession {
  sessionId: string;
  messages: ChatMessage[];
  createdAt: string;
}

export interface InvokeAgentRequest {
  message: string;
  sessionId?: string;
}

interface AgentStreamChunk {
  type: 'text' | 'structured_data' | 'done' | 'error';
  content?: string;
  data?: Record<string, unknown>;
  sessionId?: string;
}

export async function invokeAgentStream(
  request: InvokeAgentRequest,
  onChunk: (chunk: AgentStreamChunk) => void,
  signal?: AbortSignal
): Promise<void> {
  const token = await getAccessToken();

  const response = await fetch(`${API_BASE_URL}/api/v1/agent/invoke`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(request),
    signal,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || `Agent error: ${response.status}`);
  }

  if (!response.body) {
    throw new Error('No response body');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim() || !line.startsWith('data: ')) continue;
        const data = line.slice(6);
        if (data === '[DONE]') {
          onChunk({ type: 'done' });
          return;
        }
        try {
          const chunk: AgentStreamChunk = JSON.parse(data);
          onChunk(chunk);
        } catch {
          // Plain text chunk
          onChunk({ type: 'text', content: data });
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  onChunk({ type: 'done' });
}

export async function getAgentSession(sessionId: string): Promise<AgentSession> {
  const token = await getAccessToken();

  const response = await fetch(`${API_BASE_URL}/api/v1/agent/sessions/${sessionId}`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch session: ${response.status}`);
  }

  return response.json();
}
