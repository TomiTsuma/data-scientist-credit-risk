import type { EChartsOption } from "echarts";

export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
}

export interface StreamEventBase {
  type: string;
}

export interface StreamThinking extends StreamEventBase {
  type: "thinking";
  content?: string;
  reasoning?: string;
}

export interface StreamToolCall extends StreamEventBase {
  type: "tool_call";
  id?: string;
  name?: string;
  args?: Record<string, unknown>;
}

export interface StreamToolResult extends StreamEventBase {
  type: "tool_result";
  id?: string;
  name?: string;
  result?: unknown;
}

export interface StreamDone extends StreamEventBase {
  type: "done";
  message?: { content?: string };
}

export interface StreamError extends StreamEventBase {
  type: "error";
  detail?: string;
}

export type StreamEvent =
  | StreamThinking
  | StreamToolCall
  | StreamToolResult
  | StreamDone
  | StreamError;

export const ECHARTS_TOOL_NAMES = new Set([
  "create_echarts_chart",
  "create_echarts_portfolio_preset",
]);

export interface EChartsPayload {
  chartId: string;
  chartType?: string;
  title?: string;
  echartsOption: EChartsOption;
}

export function parseEChartsFromToolResult(
  toolName: string,
  result: unknown
): EChartsPayload | null {
  if (!ECHARTS_TOOL_NAMES.has(toolName)) {
    return null;
  }

  let data: Record<string, unknown>;
  if (typeof result === "string") {
    try {
      data = JSON.parse(result) as Record<string, unknown>;
    } catch {
      return null;
    }
  } else if (result && typeof result === "object") {
    data = result as Record<string, unknown>;
  } else {
    return null;
  }

  if (data.error) {
    return null;
  }

  const option = data.echartsOption;
  if (!option || typeof option !== "object") {
    return null;
  }

  return {
    chartId: String(data.chartId ?? crypto.randomUUID()),
    chartType: data.chartType as string | undefined,
    title: data.title as string | undefined,
    echartsOption: option as EChartsOption,
  };
}
