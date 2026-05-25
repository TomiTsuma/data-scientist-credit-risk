import { useCallback, useMemo, useRef, useState } from "react";
import { streamChat } from "./api/streamChat";
import { EChartBlock } from "./components/EChartBlock";
import { MarkdownMessage } from "./components/MarkdownMessage";
import {
  type ChatMessage,
  type EChartsPayload,
  parseEChartsFromToolResult,
  type StreamEvent,
} from "./types";
import "./App.css";

function newId() {
  return crypto.randomUUID();
}

export default function App() {
  const [convId] = useState(() => newId());
  const [input, setInput] = useState(
    "Show arrears by country as a chart, then summarize Kenya."
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [charts, setCharts] = useState<EChartsPayload[]>([]);
  const [status, setStatus] = useState<"idle" | "streaming" | "error">("idle");
  const [streamLog, setStreamLog] = useState<string[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const apiMessages = useMemo(
    () => messages.map((m) => ({ role: m.role, content: m.content })),
    [messages]
  );

  const appendLog = useCallback((line: string) => {
    setStreamLog((prev) => [...prev.slice(-80), line]);
  }, []);

  const handleEvent = useCallback(
    (event: StreamEvent) => {
      switch (event.type) {
        case "thinking": {
          const c = event.content || event.reasoning || "";
          if (c) appendLog(`[thinking] ${String(c).slice(0, 120)}`);
          break;
        }
        case "tool_call":
          appendLog(
            `[tool] ${event.name ?? "?"} ${JSON.stringify(event.args ?? {}).slice(0, 80)}`
          );
          break;
        case "tool_result": {
          const name = event.name ?? "";
          appendLog(`[result] ${name}`);
          const parsed = parseEChartsFromToolResult(name, event.result);
          if (parsed) {
            setCharts((prev) => {
              const exists = prev.some((c) => c.chartId === parsed.chartId);
              if (exists) {
                return prev.map((c) =>
                  c.chartId === parsed.chartId ? parsed : c
                );
              }
              return [...prev, parsed];
            });
          }
          break;
        }
        case "done": {
          const content = event.message?.content?.trim() ?? "";
          if (content) {
            setMessages((prev) => [
              ...prev,
              { id: newId(), role: "assistant", content },
            ]);
          }
          break;
        }
        case "error":
          setStatus("error");
          appendLog(`[error] ${event.detail ?? "unknown"}`);
          break;
        default:
          break;
      }
    },
    [appendLog]
  );

  const send = async () => {
    const text = input.trim();
    if (!text || status === "streaming") return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    const userMsg: ChatMessage = { id: newId(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setStatus("streaming");
    appendLog(`--- ${text.slice(0, 60)} ---`);

    const history = [
      ...apiMessages,
      { role: "user" as const, content: text },
    ];

    try {
      await streamChat({
        messages: history,
        convId,
        signal: controller.signal,
        onEvent: handleEvent,
      });
      setStatus("idle");
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setStatus("error");
        appendLog(`[error] ${(err as Error).message}`);
      } else {
        setStatus("idle");
      }
    }
  };

  const stop = () => {
    abortRef.current?.abort();
    setStatus("idle");
  };

  return (
    <div className="app">
      <header className="app__header">
        <div>
          <p className="app__eyebrow">Sunculture · AI Platform</p>
          <h1>Analytics Copilot</h1>
        </div>
        <p className="app__session">Session {convId.slice(0, 8)}…</p>
      </header>

      <div className="app__grid">
        <section className="panel panel--chat">
          <div className="messages">
            {messages.length === 0 && (
              <p className="messages__empty">
                Ask for portfolio KPIs or charts. The assistant can call{" "}
                <code>create_echarts_chart</code> — charts appear on the right.
              </p>
            )}
            {messages.map((m) => (
              <div key={m.id} className={`msg msg--${m.role}`}>
                <span className="msg__role">{m.role}</span>
                <div className="msg__body">
                  <MarkdownMessage content={m.content} />
                </div>
              </div>
            ))}
            {status === "streaming" && (
              <div className="msg msg--assistant msg--draft">
                <span className="msg__role">assistant</span>
                <div className="msg__body">Thinking and calling tools…</div>
              </div>
            )}
          </div>

          <div className="composer">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              rows={3}
              placeholder="e.g. Chart arrears by country and list top segments in Kenya"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void send();
                }
              }}
            />
            <div className="composer__actions">
              <button
                type="button"
                className="btn btn--primary"
                onClick={() => void send()}
                disabled={status === "streaming"}
              >
                {status === "streaming" ? "Streaming…" : "Send"}
              </button>
              {status === "streaming" && (
                <button type="button" className="btn btn--ghost" onClick={stop}>
                  Stop
                </button>
              )}
            </div>
          </div>

          <details className="stream-log">
            <summary>Stream events</summary>
            <pre>{streamLog.join("\n")}</pre>
          </details>
        </section>

        <section className="panel panel--charts">
          <h2>Charts</h2>
          <p className="panel__hint">
            Rendered from <code>tool_result</code> for ECharts MCP tools.
          </p>
          {charts.length === 0 ? (
            <p className="charts__empty">
              No charts yet. Try: &quot;Use create_echarts_portfolio_preset for
              arrears_by_country&quot;
            </p>
          ) : (
            <div className="charts__list">
              {charts.map((c) => (
                <EChartBlock key={c.chartId} chart={c} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
