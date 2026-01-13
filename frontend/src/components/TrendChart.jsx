import React from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// 格式化大数字
const formatNumber = (value) => {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}k`;
  }
  return value;
};

// 自定义Tooltip - 白色风格
const CustomTooltip = ({ active, payload, label, dailyColor, totalColor }) => {
  if (active && payload && payload.length) {
    return (
      <div 
        className="px-4 py-3 rounded-lg"
        style={{ 
          background: '#ffffff',
          border: '1px solid rgba(0,0,0,0.1)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}
      >
        <p className="text-gray-500 text-xs mb-2 pb-2 border-b border-gray-200 font-mono">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2" style={{ backgroundColor: entry.color }} />
            <span className="text-gray-500 text-xs uppercase">{entry.name}</span>
            <span className="text-gray-800 font-mono font-bold text-sm ml-auto">{entry.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

/**
 * 趋势图组件 - 棱角线条风格
 */
const TrendChart = ({ 
  data, 
  title, 
  dailyColor = '#fbbf24', 
  totalColor = '#22d3ee',
  icon = '📈',
  dailyLabel = '每日新增',
  totalLabel = '累计总量'
}) => {
  const chartData = data?.labels?.map((label, index) => ({
    date: label,
    daily: data.values?.[index] || 0,
    total: data.totals?.[index] || 0,
  })) || [];

  const totalDaily = chartData.reduce((sum, item) => sum + item.daily, 0);
  const maxDaily = Math.max(...chartData.map(item => item.daily), 0);
  const latestTotal = chartData.length > 0 ? chartData[chartData.length - 1].total : 0;
  const avgDaily = chartData.length > 0 ? Math.round(totalDaily / chartData.length) : 0;
  
  const totalValues = chartData.map(item => item.total).filter(v => v > 0);
  const minTotal = totalValues.length > 0 ? Math.min(...totalValues) : 0;
  const maxTotal = totalValues.length > 0 ? Math.max(...totalValues) : 0;
  const yAxisMinTotal = Math.max(0, Math.floor(minTotal - 100));
  const yAxisMaxTotal = Math.ceil(maxTotal + 100);

  if (!data || !data.labels || data.labels.length === 0) {
    return (
      <div className="bg-white p-6 border border-gray-200 rounded-xl shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-1 h-6 bg-gray-300" />
          <h3 className="text-gray-700 uppercase tracking-widest text-sm">{title}</h3>
        </div>
        <div className="h-72 flex items-center justify-center">
          <p className="text-gray-400 text-sm uppercase tracking-widest">NO DATA</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden relative shadow-sm">
      {/* 标题栏 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-1 h-6 rounded" style={{ backgroundColor: totalColor }} />
          <div>
            <h3 className="text-slate-600 uppercase tracking-widest text-sm font-medium">{title}</h3>
            <p className="text-slate-400 text-xs mt-0.5">Time Series Analysis</p>
          </div>
        </div>
        
        {/* 统计指标 */}
        <div className="flex gap-6">
          <div className="text-right">
            <p className="text-slate-400 text-[10px] uppercase tracking-widest">TOTAL</p>
            <p className="font-mono font-bold text-lg" style={{ color: totalColor }}>
              {formatNumber(latestTotal)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-slate-400 text-[10px] uppercase tracking-widest">AVG/DAY</p>
            <p className="font-mono font-bold text-lg" style={{ color: dailyColor }}>
              {formatNumber(avgDaily)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-slate-400 text-[10px] uppercase tracking-widest">PEAK</p>
            <p className="font-mono font-bold text-lg" style={{ color: dailyColor }}>
              {formatNumber(maxDaily)}
            </p>
          </div>
        </div>
      </div>

      {/* 图例 */}
      <div className="flex gap-6 px-4 py-2 border-b border-gray-100 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-2 rounded-sm" style={{ backgroundColor: dailyColor }} />
          <span className="text-gray-500 uppercase tracking-wider">{dailyLabel}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-0.5" style={{ backgroundColor: totalColor }} />
          <span className="text-gray-500 uppercase tracking-wider">{totalLabel}</span>
        </div>
      </div>

      {/* 图表 */}
      <div className="h-64 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(0, 0, 0, 0.06)" 
              vertical={true}
            />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              fontSize={10}
              tickLine={false}
              axisLine={{ stroke: 'rgba(0, 0, 0, 0.1)' }}
              tickFormatter={(value) => {
                if (value && value.length > 7) {
                  return value.substring(5);
                }
                return value;
              }}
              interval="preserveStartEnd"
            />
            <YAxis 
              yAxisId="left"
              stroke="#9ca3af"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tickFormatter={formatNumber}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              stroke="#9ca3af"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tickFormatter={formatNumber}
              domain={[yAxisMinTotal, yAxisMaxTotal]}
              tickCount={5}
            />
            <Tooltip 
              content={<CustomTooltip dailyLabel={dailyLabel} totalLabel={totalLabel} dailyColor={dailyColor} totalColor={totalColor} />}
              cursor={{ stroke: 'rgba(0, 0, 0, 0.1)' }}
            />
            {/* 每日新增 - 柱状图（圆角） */}
            <Bar
              yAxisId="left"
              dataKey="daily"
              name={dailyLabel}
              fill={dailyColor}
              opacity={0.8}
              radius={[2, 2, 0, 0]}
            />
            {/* 累计总量 - 折线图（平滑曲线） */}
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="total"
              name={totalLabel}
              stroke={totalColor}
              strokeWidth={2}
              dot={false}
              activeDot={{ 
                r: 4, 
                stroke: totalColor, 
                strokeWidth: 2, 
                fill: '#ffffff',
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TrendChart;
