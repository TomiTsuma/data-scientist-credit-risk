import ReactECharts from "echarts-for-react";
import type { EChartsOption } from "echarts";
import type { EChartsPayload } from "../types";

interface EChartBlockProps {
  chart: EChartsPayload;
}

export function EChartBlock({ chart }: EChartBlockProps) {
  const option = chart.echartsOption as EChartsOption;
  const displayTitle =
    chart.title ||
    (typeof option.title === "object" && option.title && "text" in option.title
      ? String((option.title as { text?: string }).text)
      : "Chart");

  return (
    <article className="chart-card">
      <header className="chart-card__header">
        <h3>{displayTitle}</h3>
        {chart.chartType && (
          <span className="chart-card__badge">{chart.chartType}</span>
        )}
      </header>
      <ReactECharts
        option={option}
        style={{ height: 360, width: "100%" }}
        notMerge
        lazyUpdate
        opts={{ renderer: "canvas" }}
      />
    </article>
  );
}
