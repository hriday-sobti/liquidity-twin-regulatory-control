import ReactECharts from 'echarts-for-react';

interface MovementWaterfallProps {
  previousNsfr: number;
  currentNsfr: number;
  totalMovement: number;
  drivers: Array<{
    driver_name: string;
    contribution_pp: number;
    balance_movement_usd: number;
    impact_direction: string;
  }>;
  onDriverClick?: (driverName: string) => void;
}

export default function MovementWaterfall({
  previousNsfr,
  currentNsfr,
  totalMovement,
  drivers,
  onDriverClick,
}: MovementWaterfallProps) {
  const categories = ['Prior NSFR', ...drivers.map((d) => d.driver_name), 'Current NSFR'];
  
  const baseData: number[] = [];
  const positiveData: (number | string)[] = [];
  const negativeData: (number | string)[] = [];

  let running = previousNsfr;
  baseData.push(0);
  positiveData.push(previousNsfr);
  negativeData.push('-');

  drivers.forEach((d) => {
    const val = d.contribution_pp;
    if (val >= 0) {
      baseData.push(running);
      positiveData.push(val);
      negativeData.push('-');
      running += val;
    } else {
      running += val;
      baseData.push(running);
      positiveData.push('-');
      negativeData.push(Math.abs(val));
    }
  });

  baseData.push(0);
  positiveData.push(currentNsfr);
  negativeData.push('-');

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => {
        const arr = Array.isArray(params) ? params : [];
        const item = arr[1] && typeof arr[1] === 'object' && 'value' in arr[1] && arr[1].value !== '-' ? arr[1] : arr[2];
        if (!item || typeof item !== 'object' || !('name' in item) || !('value' in item)) return '';
        const val = typeof item.value === 'number' ? item.value : 0;
        return `<div class="font-mono text-xs p-1">
          <b>${String(item.name)}</b><br/>
          Impact: ${val > 0 ? '+' : ''}${val.toFixed(2)} pp
        </div>`;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '12%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0,
        rotate: 25,
        fontSize: 10,
        color: '#667085',
        fontFamily: 'Inter',
      },
      axisLine: { lineStyle: { color: '#D9DEE5' } },
    },
    yAxis: {
      type: 'value',
      min: Math.floor(Math.min(previousNsfr, currentNsfr) - 2),
      max: Math.ceil(Math.max(previousNsfr, currentNsfr) + 2),
      axisLabel: {
        formatter: '{value}%',
        fontSize: 10,
        color: '#667085',
        fontFamily: 'JetBrains Mono',
      },
      splitLine: { lineStyle: { color: '#F2F4F7' } },
    },
    series: [
      {
        name: 'Placeholder',
        type: 'bar',
        stack: 'Total',
        itemStyle: { borderColor: 'transparent', color: 'transparent' },
        emphasis: { itemStyle: { borderColor: 'transparent', color: 'transparent' } },
        data: baseData,
      },
      {
        name: 'Increase',
        type: 'bar',
        stack: 'Total',
        itemStyle: { color: '#2E7D32', borderRadius: [2, 2, 0, 0] },
        data: positiveData,
      },
      {
        name: 'Decrease',
        type: 'bar',
        stack: 'Total',
        itemStyle: { color: '#B42318', borderRadius: [2, 2, 0, 0] },
        data: negativeData,
      },
    ],
  };

  const onChartClick = (params: unknown) => {
    if (params && typeof params === 'object' && 'name' in params && typeof params.name === 'string') {
      if (params.name !== 'Prior NSFR' && params.name !== 'Current NSFR') {
        onDriverClick?.(params.name);
      }
    }
  };

  return (
    <div className="bg-surface p-4 rounded-lg border border-border">
      <div className="flex justify-between items-center mb-2">
        <div>
          <h2 className="text-sm font-semibold text-text">WHAT CHANGED? — NSFR Movement Waterfall</h2>
          <p className="text-xs text-muted">
            Decomposition from Prior Period ({previousNsfr.toFixed(2)}%) to Current ({currentNsfr.toFixed(2)}%):{' '}
            <span className={`font-mono font-semibold ${totalMovement >= 0 ? 'text-success' : 'text-danger'}`}>
              {totalMovement >= 0 ? '+' : ''}
              {totalMovement.toFixed(2)} pp
            </span>
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-success inline-block"></span>
            <span>Accretive</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-danger inline-block"></span>
            <span>Dilutive</span>
          </div>
        </div>
      </div>

      <div className="h-[260px] w-full">
        <ReactECharts
          option={option}
          style={{ height: '100%', width: '100%' }}
          onEvents={{ click: onChartClick }}
        />
      </div>
    </div>
  );
}
