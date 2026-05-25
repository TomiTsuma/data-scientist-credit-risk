import type { StreamEvent } from "../types";

const STREAM_URL = "/api/ai/v1/chat/stream";

export interface StreamChatOptions {
  messages: { role: string; content: string }[];
  convId: string;
  provider?: string;
  model?: string;
  signal?: AbortSignal;
  onEvent: (event: StreamEvent) => void;
}

export async function streamChat({
  messages,
  convId,
  provider,
  model,
  signal,
  onEvent,
}: StreamChatOptions): Promise<void> {
  const payload: Record<string, unknown> = {
    messages,
    conv_id: convId,
  };
  if (provider) payload.provider = provider;
  if (model) payload.model = model;

  const response = await fetch(STREAM_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Stream failed (${response.status}): ${text}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    let newlineIndex: number;
    while ((newlineIndex = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, newlineIndex).trim();
      buffer = buffer.slice(newlineIndex + 1);
      if (!line.startsWith("data: ")) continue;
      const raw = line.slice(6);
      if (!raw) continue;
      try {
        const parsed = JSON.parse(raw) as { type?: string };
        if (parsed?.type) {
          onEvent(parsed as StreamEvent);
        }
      } catch {
        /* skip malformed SSE chunks */
      }
    }
  }
}
