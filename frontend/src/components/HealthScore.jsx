import React, { useState, useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import SimilarProjectsModal from './SimilarProjectsModal';

// 饼状图颜色
const PIE_COLORS = ['#22c55e', '#f59e0b', '#3b82f6', '#a855f7', '#ec4899', '#14b8a6'];

/**
 * 四维雷达图组件 - 白色背景风格
 */
const RadarChart = ({ dimensions, gradeColor }) => {
  const [hoveredIndex, setHoveredIndex] = useState(null);
  
  const size = 280;
  const center = size / 2;
  const maxRadius = 90;
  
  // 四个维度配置
  const axes = [
    { key: 'growth', label: '关注度', angle: -90, color: '#22c55e' },
    { key: 'activity', label: '活跃度', angle: 0, color: '#f97316' },
    { key: 'contribution', label: '贡献度', angle: 90, color: '#3b82f6' },
    { key: 'code', label: '代码', angle: 180, color: '#a855f7' },
  ];
  
  const scores = axes.map(axis => {
    const dim = dimensions?.[axis.key];
    return dim?.score || 0;
  });
  
  const getPoint = (angle, value) => {
    const rad = (angle * Math.PI) / 180;
    const r = (value / 100) * maxRadius;
    return {
      x: center + r * Math.cos(rad),
      y: center + r * Math.sin(rad),
    };
  };
  
  const dataPoints = axes.map((axis, i) => getPoint(axis.angle, scores[i]));
  const dataPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
  
  const gridLevels = [25, 50, 75, 100];
  
  return (
    <div className="relative">
      <svg width={size} height={size} className="overflow-visible">
        <defs>
          {/* 渐变定义 */}
          <radialGradient id="radarBgGradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(0,0,0,0.02)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0)" />
          </radialGradient>
          <linearGradient id="radarStrokeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={gradeColor} stopOpacity="0.6" />
            <stop offset="100%" stopColor={gradeColor} stopOpacity="0.2" />
          </linearGradient>
        </defs>
        
        {/* 最外层圆形边框 */}
        <circle 
          cx={center} 
          cy={center} 
          r={maxRadius + 18} 
          fill="none" 
          stroke="rgba(0,0,0,0.06)" 
          strokeWidth="1"
        />
        <circle 
          cx={center} 
          cy={center} 
          r={maxRadius + 12} 
          fill="url(#radarBgGradient)" 
          stroke="rgba(0,0,0,0.04)" 
          strokeWidth="1"
        />
        
        {/* 圆形网格 */}
        {gridLevels.map((level, i) => (
          <circle
            key={i}
            cx={center}
            cy={center}
            r={(level / 100) * maxRadius}
            fill="none"
            stroke={i === gridLevels.length - 1 ? "rgba(0,0,0,0.12)" : "rgba(0,0,0,0.06)"}
            strokeWidth="1"
            strokeDasharray={i < gridLevels.length - 1 ? "3 3" : "none"}
          />
        ))}
        
        {/* 轴线 */}
        {axes.map((axis, i) => {
          const endPoint = getPoint(axis.angle, 100);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={endPoint.x}
              y2={endPoint.y}
              stroke={axis.color}
              strokeWidth="1"
              opacity="0.3"
            />
          );
        })}
        
        {/* 数据区域填充 */}
        <path
          d={dataPath}
          fill={gradeColor}
          fillOpacity="0.15"
          stroke="none"
        />
        
        {/* 数据区域边框 */}
        <path
          d={dataPath}
          fill="none"
          stroke={gradeColor}
          strokeWidth="2.5"
          strokeLinejoin="round"
          className="transition-all duration-300"
          style={{ filter: `drop-shadow(0 0 6px ${gradeColor}40)` }}
        />
        
        {/* 数据点 - 圆形 */}
        {dataPoints.map((point, i) => {
          const isHovered = hoveredIndex === i;
          const pointSize = isHovered ? 8 : 6;
          return (
            <g key={i}>
              {/* 光晕效果 */}
              <circle
                cx={point.x}
                cy={point.y}
                r={pointSize + 4}
                fill={axes[i].color}
                opacity={isHovered ? 0.3 : 0.1}
                className="transition-all duration-200"
              />
              <circle
                cx={point.x}
                cy={point.y}
                r={pointSize}
                fill={isHovered ? axes[i].color : "#ffffff"}
                stroke={axes[i].color}
                strokeWidth="2"
                className="transition-all duration-200 cursor-pointer"
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              />
            </g>
          );
        })}
        
        {/* 轴标签 */}
        {axes.map((axis, i) => {
          const labelPoint = getPoint(axis.angle, 135);
          const score = scores[i];
          const isHovered = hoveredIndex === i;
          
          // 根据角度调整文本位置
          let textAnchor = "middle";
          let dx = 0;
          if (axis.angle === 0) { textAnchor = "start"; dx = 8; }
          if (axis.angle === 180) { textAnchor = "end"; dx = -8; }
          
          return (
            <g 
              key={`label-${i}`} 
              className="cursor-pointer" 
              onMouseEnter={() => setHoveredIndex(i)} 
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <text
                x={labelPoint.x + dx}
                y={labelPoint.y - 8}
                textAnchor={textAnchor}
                fill={isHovered ? axis.color : "#6b7280"}
                className="uppercase tracking-widest transition-colors duration-200"
                style={{ fontSize: '10px', fontWeight: '600', letterSpacing: '0.08em' }}
              >
                {axis.label}
              </text>
              <text
                x={labelPoint.x + dx}
                y={labelPoint.y + 12}
                textAnchor={textAnchor}
                fill={isHovered ? axis.color : "#374151"}
                className="font-mono transition-colors duration-200"
                style={{ fontSize: '18px', fontWeight: '700' }}
              >
                {score.toFixed(0)}
              </text>
            </g>
          );
        })}
        
        {/* 中心圆形 */}
        <circle
          cx={center}
          cy={center}
          r={28}
          fill="#ffffff"
          stroke={gradeColor}
          strokeWidth="2"
          style={{ filter: `drop-shadow(0 0 8px ${gradeColor}30)` }}
        />
        <text 
          x={center} 
          y={center + 6} 
          textAnchor="middle" 
          fill={gradeColor} 
          className="font-mono"
          style={{ fontSize: '16px', fontWeight: '700' }}
        >
          {(scores.reduce((a, b) => a + b, 0) / 4).toFixed(0)}
        </text>
      </svg>
      
      {/* 悬停提示 */}
      {hoveredIndex !== null && (
        <div 
          className="absolute px-4 py-2 text-xs pointer-events-none z-20 rounded-lg"
          style={{
            background: 'rgba(255,255,255,0.98)',
            border: `1px solid ${axes[hoveredIndex].color}50`,
            boxShadow: `0 4px 20px rgba(0,0,0,0.1)`,
            left: '50%',
            bottom: '-50px',
            transform: 'translateX(-50%)',
          }}
        >
          <span className="text-gray-500">{axes[hoveredIndex].label}：</span>
          <span className="font-mono font-bold ml-1" style={{ color: axes[hoveredIndex].color }}>
            {scores[hoveredIndex].toFixed(1)}
          </span>
        </div>
      )}
    </div>
  );
};

/**
 * 圆形水滴填充进度指示器
 */
const LiquidProgress = ({ score, size = 200, color }) => {
  const center = size / 2;
  const radius = size / 2 - 20;
  const innerRadius = radius - 12;
  
  // 计算填充高度（从底部开始）
  const fillPercent = Math.min(100, Math.max(0, score)) / 100;
  const fillHeight = innerRadius * 2 * fillPercent;
  const fillY = center + innerRadius - fillHeight;
  
  // 进度环的周长和偏移
  const circumference = 2 * Math.PI * radius;
  const progressOffset = circumference * (1 - fillPercent);
  
  // 波浪动画路径
  const waveAmplitude = 4;
  const waveLength = 40;
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="overflow-visible">
        <defs>
          {/* 渐变填充 */}
          <linearGradient id="liquidGradient" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor={color} stopOpacity="0.9" />
            <stop offset="50%" stopColor={color} stopOpacity="0.6" />
            <stop offset="100%" stopColor={color} stopOpacity="0.3" />
          </linearGradient>
          
          {/* 圆形裁剪 */}
          <clipPath id="liquidClip">
            <circle cx={center} cy={center} r={innerRadius} />
          </clipPath>
          
          {/* 发光效果 */}
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* 最外层装饰圆 */}
        <circle 
          cx={center} 
          cy={center} 
          r={radius + 15} 
          fill="none" 
          stroke="rgba(0,0,0,0.05)" 
          strokeWidth="1"
        />
        
        {/* 外层光晕圆 */}
        <circle 
          cx={center} 
          cy={center} 
          r={radius + 8} 
          fill="none" 
          stroke={color}
          strokeWidth="1"
          opacity="0.2"
        />
        
        {/* 背景圆环 */}
        <circle 
          cx={center} 
          cy={center} 
          r={radius} 
          fill="none" 
          stroke="rgba(0,0,0,0.08)" 
          strokeWidth="4"
        />
        
        {/* 进度圆环 */}
        <circle 
          cx={center} 
          cy={center} 
          r={radius} 
          fill="none" 
          stroke={color}
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={progressOffset}
          transform={`rotate(-90 ${center} ${center})`}
          className="transition-all duration-1000"
          style={{ filter: `drop-shadow(0 0 6px ${color}60)` }}
        />
        
        {/* 内部背景圆 */}
        <circle 
          cx={center} 
          cy={center} 
          r={innerRadius} 
          fill="#f8fafc"
          stroke="rgba(0,0,0,0.06)"
          strokeWidth="1"
        />
        
        {/* 水滴填充 */}
        <g clipPath="url(#liquidClip)">
          {/* 主填充区域 */}
          <rect 
            x={center - innerRadius} 
            y={fillY} 
            width={innerRadius * 2} 
            height={fillHeight + 10}
            fill="url(#liquidGradient)"
            className="transition-all duration-1000"
          />
          
          {/* 波浪效果 - 第一层 */}
          <path
            d={`M ${center - innerRadius - 10} ${fillY}
                Q ${center - innerRadius/2} ${fillY - waveAmplitude} ${center} ${fillY}
                Q ${center + innerRadius/2} ${fillY + waveAmplitude} ${center + innerRadius + 10} ${fillY}
                L ${center + innerRadius + 10} ${center + innerRadius + 10}
                L ${center - innerRadius - 10} ${center + innerRadius + 10} Z`}
            fill={color}
            opacity="0.4"
            className="transition-all duration-1000"
          >
            <animate 
              attributeName="d" 
              dur="3s" 
              repeatCount="indefinite"
              values={`
                M ${center - innerRadius - 10} ${fillY}
                Q ${center - innerRadius/2} ${fillY - waveAmplitude} ${center} ${fillY}
                Q ${center + innerRadius/2} ${fillY + waveAmplitude} ${center + innerRadius + 10} ${fillY}
                L ${center + innerRadius + 10} ${center + innerRadius + 10}
                L ${center - innerRadius - 10} ${center + innerRadius + 10} Z;
                M ${center - innerRadius - 10} ${fillY}
                Q ${center - innerRadius/2} ${fillY + waveAmplitude} ${center} ${fillY}
                Q ${center + innerRadius/2} ${fillY - waveAmplitude} ${center + innerRadius + 10} ${fillY}
                L ${center + innerRadius + 10} ${center + innerRadius + 10}
                L ${center - innerRadius - 10} ${center + innerRadius + 10} Z;
                M ${center - innerRadius - 10} ${fillY}
                Q ${center - innerRadius/2} ${fillY - waveAmplitude} ${center} ${fillY}
                Q ${center + innerRadius/2} ${fillY + waveAmplitude} ${center + innerRadius + 10} ${fillY}
                L ${center + innerRadius + 10} ${center + innerRadius + 10}
                L ${center - innerRadius - 10} ${center + innerRadius + 10} Z
              `}
            />
          </path>
          
          {/* 高光效果 */}
          <ellipse
            cx={center - innerRadius * 0.3}
            cy={fillY + fillHeight * 0.3}
            rx={innerRadius * 0.15}
            ry={fillHeight * 0.2}
            fill="rgba(255,255,255,0.1)"
            className="transition-all duration-1000"
          />
        </g>
        
        {/* 中心小圆点装饰 */}
        <circle
          cx={center}
          cy={center}
          r={4}
          fill={color}
          opacity="0.5"
        />
      </svg>
      
      {/* 分数文字 */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span 
          className="font-mono text-5xl font-bold"
          style={{ 
            color,
            textShadow: `0 0 20px ${color}30`
          }}
        >
          {score.toFixed(1)}
        </span>
        <span className="text-slate-400 text-xs uppercase tracking-widest mt-2">HEALTH SCORE</span>
      </div>
    </div>
  );
};

// 维度饼状图 Tooltip
const DimensionPieTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div 
        className="px-4 py-3 rounded-lg"
        style={{ 
          background: 'rgba(255,255,255,0.98)',
          border: '1px solid rgba(0,0,0,0.1)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          backdropFilter: 'blur(10px)'
        }}
      >
        <p className="text-gray-800 text-xs font-medium mb-2">{data.name}</p>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-gray-500 text-xs">值</span>
          <span className="text-gray-800 font-mono text-xs">{data.displayValue}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-xs">占比</span>
          <span className="font-mono text-xs" style={{ color: data.fill }}>{data.percentage.toFixed(1)}%</span>
        </div>
      </div>
    );
  }
  return null;
};

// 获取维度的饼状图数据
const getDimensionPieData = (dimensionKey, dimension) => {
  const details = dimension?.details || {};
  
  switch (dimensionKey) {
    case 'growth':
      // 关注度增长：Star和Fork的得分
      return [
        { name: 'Star增长得分', value: dimension.star_score || 0, displayValue: (dimension.star_score || 0).toFixed(1) },
        { name: 'Fork增长得分', value: dimension.fork_score || 0, displayValue: (dimension.fork_score || 0).toFixed(1) },
      ];
    case 'activity':
      // 开发活跃度：Commit趋势和OpenDigger
      return [
        { name: 'Commit趋势得分', value: dimension.commit_trend_score || 0, displayValue: (dimension.commit_trend_score || 0).toFixed(1) },
        { name: 'OpenDigger得分', value: dimension.opendigger_score || 0, displayValue: (dimension.opendigger_score || 0).toFixed(1) },
      ];
    case 'contribution':
      // 社区贡献度：周均PR和月均PR
      return [
        { name: '周均PR', value: details.pr_avg_last_week || 0, displayValue: (details.pr_avg_last_week || 0).toFixed(1) },
        { name: '月均PR', value: details.pr_avg_month || 0, displayValue: (details.pr_avg_month || 0).toFixed(1) },
      ];
    case 'code':
      // 代码健康度：添加和删除
      return [
        { name: '代码添加', value: details.pull_additions || 0, displayValue: formatNumber(details.pull_additions || 0) },
        { name: '代码删除', value: details.pull_deletions || 0, displayValue: formatNumber(details.pull_deletions || 0) },
      ];
    default:
      return [];
  }
};

/**
 * 维度条 - 白色背景风格
 */
const DimensionBar = ({ name, score, weight, color, dimension, dimensionKey, isExpanded, onToggle }) => {
  const barWidth = Math.min(100, Math.max(0, score));
  const details = dimension?.details || {};
  
  // 获取饼状图数据
  const pieData = useMemo(() => {
    const data = getDimensionPieData(dimensionKey, dimension);
    const total = data.reduce((sum, item) => sum + (item.value || 0), 0);
    return data.map((item, index) => ({
      ...item,
      fill: PIE_COLORS[index % PIE_COLORS.length],
      percentage: total > 0 ? (item.value / total) * 100 : 0,
    }));
  }, [dimensionKey, dimension]);
  
  return (
    <div className="mb-4 group">
      <div 
        className="flex items-center justify-between mb-2 cursor-pointer hover:opacity-80 transition-opacity"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3">
          {/* 圆形指示器 */}
          <div 
            className="w-3 h-3 rounded-full"
            style={{ 
              backgroundColor: color,
              boxShadow: `0 0 8px ${color}50`
            }}
          />
          <span className="text-gray-700 text-sm font-medium">{name}</span>
          <span className="text-gray-400 text-xs">({weight})</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-gray-800 font-bold">{score.toFixed(1)}</span>
          <svg 
            className={`w-4 h-4 text-gray-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      
      {/* 进度条 - 圆角柔和风格 */}
      <div className="h-2 bg-gray-100 rounded-full relative overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${barWidth}%`,
            background: `linear-gradient(90deg, ${color}90 0%, ${color} 100%)`,
            boxShadow: `0 0 10px ${color}40`
          }}
        />
      </div>
            
      {/* 展开详情 - 包含饼状图 */}
      {isExpanded && (
        <div className="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
          <div className="flex gap-5">
            {/* 饼状图 */}
            <div className="w-28 h-28 flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={22}
                    outerRadius={42}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="#ffffff"
                    strokeWidth={2}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip content={<DimensionPieTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            {/* 图例和详情 */}
            <div className="flex-1">
              {/* 饼状图图例 */}
              <div className="mb-3 space-y-2">
                {pieData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: item.fill }} 
                      />
                      <span className="text-gray-500">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-700 font-mono">{item.displayValue}</span>
                      <span className="text-gray-400">({item.percentage.toFixed(1)}%)</span>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* 分隔线 */}
              <div className="border-t border-gray-200 my-3"></div>
              
              {/* 原始详细数据 */}
              <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
                {Object.entries(details).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-xs">
                    <span className="text-gray-500">{formatDetailKey(key)}</span>
                    <span className="text-gray-700 font-mono">{formatNumber(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const formatDetailKey = (key) => {
  const keyMap = {
    'star_current_month': '本月Star',
    'star_avg_prev_3m': '前3月均',
    'fork_current_month': '本月Fork',
    'fork_avg_prev_3m': '前3月均',
    'commit_avg_last_week': '周均Commit',
    'commit_avg_month': '月均Commit',
    'commit_ratio': '趋势比',
    'opendigger_activity': 'OD活跃度',
    'pr_avg_last_week': '周均PR',
    'pr_avg_month': '月均PR',
    'pr_ratio': 'PR趋势比',
    'pull_additions': '代码添加',
    'pull_deletions': '代码删除',
    'total_churn': '总变动量'
  };
  return keyMap[key] || key;
};

const formatNumber = (num) => {
  if (num === null || num === undefined || isNaN(num)) return '0';
  const n = Number(num);
  if (isNaN(n)) return '0';
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n.toFixed ? n.toFixed(1) : String(n);
};

/**
 * 等级徽章 - 白色背景风格
 */
const GradeBadge = ({ grade, label, color }) => {
  return (
    <div className="flex items-center gap-3">
      <div 
        className="w-12 h-12 rounded-full flex items-center justify-center border-2 relative"
        style={{ 
          borderColor: color,
          background: `radial-gradient(circle at 30% 30%, ${color}15 0%, #ffffff 70%)`,
          boxShadow: `0 0 15px ${color}20`
        }}
      >
        {/* 内部光晕 */}
        <div 
          className="absolute inset-1 rounded-full"
          style={{ background: `radial-gradient(circle at 50% 50%, ${color}10 0%, transparent 70%)` }}
        />
        <span className="font-mono text-2xl font-bold relative z-10" style={{ color }}>{grade}</span>
      </div>
      <div className="flex flex-col">
        <span className="text-gray-700 text-sm font-medium">{label}</span>
        <span className="text-gray-400 text-xs">等级评定</span>
      </div>
    </div>
  );
};

/**
 * 健康度评分主组件 - 白色卡片风格
 */
const HealthScore = ({ data, isLoading = false, projectName }) => {
  const [expandedDimension, setExpandedDimension] = useState(null);
  const [showModal, setShowModal] = useState(false);
  
  const dimensionConfig = useMemo(() => [
    { key: 'growth', color: '#22c55e' },
    { key: 'activity', color: '#f97316' },
    { key: 'contribution', color: '#3b82f6' },
    { key: 'code', color: '#a855f7' }
  ], []);
  
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-8 h-8 rounded-full bg-gray-100 animate-pulse" />
          <h3 className="text-gray-700 uppercase tracking-widest text-sm">健康度评估</h3>
        </div>
        <div className="flex items-center justify-center py-12">
          <div className="w-40 h-40 rounded-full border border-gray-200 animate-pulse" />
        </div>
      </div>
    );
  }
  
  if (!data) {
    return (
      <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
            <span className="text-gray-400 text-sm">?</span>
          </div>
          <h3 className="text-gray-700 uppercase tracking-widest text-sm">健康度评估</h3>
        </div>
        <div className="text-center py-8 text-gray-400 text-sm">
          NO DATA
        </div>
      </div>
    );
  }
  
  const { final_score, grade, grade_label, grade_color, dimensions } = data;
  
  return (
    <div 
      className="bg-white rounded-3xl border border-gray-200 overflow-hidden relative shadow-sm"
    >
      {/* 标题栏 */}
      <div 
        className="flex items-center justify-between p-5 border-b border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors relative z-10"
        onClick={() => setShowModal(true)}
      >
        <div className="flex items-center gap-4">
          {/* 圆形图标 */}
          <div 
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ 
              background: `linear-gradient(135deg, ${grade_color}20 0%, ${grade_color}08 100%)`,
              border: `1px solid ${grade_color}30`
            }}
          >
            <span className="text-lg">🏥</span>
          </div>
          <div>
            <h3 className="text-slate-600 uppercase tracking-widest text-sm font-medium">
              PROJECT HEALTH
            </h3>
            <p className="text-slate-400 text-xs mt-0.5">PHAM v2.0 Analysis</p>
          </div>
        </div>
        <GradeBadge grade={grade} label={grade_label} color={grade_color} />
      </div>
      
      {/* 主内容区 */}
      <div className="p-6 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 左侧：圆形水滴进度 */}
          <div className="flex flex-col items-center justify-center">
            <LiquidProgress score={final_score} size={200} color={grade_color} />
          </div>
          
          {/* 中间：四维雷达图 */}
          <div className="flex flex-col items-center justify-center">
            <div className="text-slate-500 text-xs uppercase tracking-widest mb-2">DIMENSION MAP</div>
            <RadarChart dimensions={dimensions} gradeColor={grade_color} />
          </div>
        
          {/* 右侧：维度详情 */}
          <div className="w-full">
            <div className="text-slate-500 text-xs uppercase tracking-widest mb-4">METRICS</div>
            {dimensionConfig.map(({ key, color }) => {
              const dim = dimensions[key];
              if (!dim) return null;
              
              return (
                <DimensionBar
                  key={key}
                  name={dim.name}
                  score={dim.score}
                  weight={dim.weight}
                  color={color}
                  dimension={dim}
                  dimensionKey={key}
                  isExpanded={expandedDimension === key}
                  onToggle={() => setExpandedDimension(expandedDimension === key ? null : key)}
                />
              );
            })}
          </div>
        </div>
      </div>
      
      {/* 底部信息栏 */}
      <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500 relative z-10">
        <div className="flex items-center gap-4">
          <span>权重分配</span>
          <div className="flex items-center gap-3">
            {dimensionConfig.map(({ key, color }) => (
              <div key={key} className="flex items-center gap-1.5">
                <div 
                  className="w-2.5 h-2.5 rounded-full" 
                  style={{ backgroundColor: color, boxShadow: `0 0 6px ${color}50` }} 
                />
                <span>20%</span>
              </div>
            ))}
          </div>
        </div>
        {data.calculated_at && (
          <span className="font-mono text-gray-500">{new Date(data.calculated_at).toLocaleString('zh-CN')}</span>
        )}
      </div>
      
      {/* 相似项目模态框 */}
      <SimilarProjectsModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        projectName={projectName || data?.project}
        currentScore={final_score}
        currentGrade={grade}
      />
    </div>
  );
};

export default HealthScore;
