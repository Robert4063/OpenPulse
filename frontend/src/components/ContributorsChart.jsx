import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

// 固定颜色方案 - 橙色主题风格
const COLORS = [
  '#f97316', // 橙色
  '#22d3ee', // 青色  
  '#fbbf24', // 黄色
  '#f43f5e', // 粉红
  '#10b981', // 绿色
  '#6366f1', // 靛蓝
  '#a855f7', // 紫色
  '#ec4899', // 玫红
  '#14b8a6', // 蓝绿
  '#8b5cf6', // 紫罗兰
];

// 自定义Tooltip - 白色风格
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const avatarUrl = `https://avatars.githubusercontent.com/${data.name}?s=48`;
    return (
      <div 
        className="px-4 py-3 rounded-lg"
        style={{ 
          background: '#ffffff',
          border: '1px solid rgba(0,0,0,0.1)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}
      >
        <div className="flex items-center gap-3 mb-2">
          <img 
            src={avatarUrl} 
            alt={data.name}
            className="w-8 h-8 rounded-full border"
            style={{ borderColor: data.color }}
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <p className="font-medium text-gray-800 font-mono">{data.name}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-xs uppercase">Commits</span>
          <span className="text-gray-800 font-mono font-bold">{data.value}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-xs uppercase">Ratio</span>
          <span className="text-orange-500 font-mono">{data.percentage?.toFixed(1)}%</span>
        </div>
      </div>
    );
  }
  return null;
};

/**
 * 活跃贡献者图表组件 - 棱角线条风格
 */
const ContributorsChart = ({ data, totalContributors, totalCommits }) => {
  const contributors = data?.contributors || [];
  
  // 构建饼图数据
  const totalComments = contributors.reduce((sum, c) => sum + (c.comment_count || c.commit_count || 0), 0);
  const pieData = contributors.map((c, index) => ({
    name: c.username || c.user_name || 'Unknown',
    value: c.comment_count || c.commit_count || 0,
    color: COLORS[index % COLORS.length],
    percentage: totalComments > 0 ? (((c.comment_count || c.commit_count || 0)) / totalComments * 100) : 0,
  }));

  // 空数据
  if (!contributors || contributors.length === 0) {
    return (
      <div className="bg-white p-6 border border-gray-200 rounded-xl shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-1 h-6 bg-gray-300" />
          <h3 className="text-gray-700 uppercase tracking-widest text-sm">活跃贡献者</h3>
        </div>
        <div className="h-52 flex items-center justify-center">
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
          <div className="w-1 h-6 bg-orange-500 rounded" />
          <div>
            <h3 className="text-slate-600 uppercase tracking-widest text-sm font-medium">CONTRIBUTORS</h3>
            <p className="text-slate-400 text-xs mt-0.5">Top Active Members</p>
          </div>
        </div>
        
        {/* 统计指标 */}
        <div className="flex gap-6">
          <div className="text-right">
            <p className="text-slate-400 text-[10px] uppercase tracking-widest">TOTAL</p>
            <p className="font-mono font-bold text-lg text-orange-500">
              {totalContributors || contributors.length}
            </p>
          </div>
          <div className="text-right">
            <p className="text-slate-400 text-[10px] uppercase tracking-widest">COMMENTS</p>
            <p className="font-mono font-bold text-lg text-amber-600">
              {totalComments.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
        {/* 饼图 */}
        <div className="h-56 relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
                stroke="#ffffff"
                strokeWidth={2}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          {/* 中心文字 */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <p className="text-gray-500 text-xs uppercase tracking-widest">TOP</p>
            <p className="text-gray-800 font-mono font-bold text-2xl">{pieData.length}</p>
          </div>
        </div>

        {/* 贡献者列表 */}
        <div className="space-y-2 max-h-56 overflow-y-auto">
          {contributors.map((contributor, index) => {
            const username = contributor.username || contributor.user_name || 'Unknown';
            const githubUrl = contributor.github_url || `https://github.com/${username}`;
            const avatarUrl = `https://avatars.githubusercontent.com/${username}?s=64`;
            const count = contributor.comment_count || contributor.commit_count || 0;
            
            return (
              <a 
                key={index} 
                href={githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 group hover:bg-gray-50 p-2 -mx-2 transition-all cursor-pointer rounded"
                title={`查看 ${username} 的 GitHub 主页`}
              >
                {/* 排名 */}
                <div 
                  className="w-6 h-6 flex items-center justify-center text-xs font-mono flex-shrink-0 rounded"
                  style={{ 
                    backgroundColor: COLORS[index % COLORS.length] + '20',
                    color: COLORS[index % COLORS.length]
                  }}
                >
                  {index + 1}
                </div>
                
                {/* 头像 */}
                <div className="relative flex-shrink-0">
                  <img 
                    src={avatarUrl}
                    alt={username}
                    className="w-8 h-8 rounded-full border-2 transition-all group-hover:border-orange-400"
                    style={{ borderColor: COLORS[index % COLORS.length] + '40' }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  {/* 头像加载失败时的占位符 */}
                  <div 
                    className="w-8 h-8 rounded-full border-2 items-center justify-center text-xs font-mono hidden"
                    style={{ 
                      backgroundColor: COLORS[index % COLORS.length] + '20',
                      borderColor: COLORS[index % COLORS.length] + '40',
                      color: COLORS[index % COLORS.length]
                    }}
                  >
                    {username.charAt(0).toUpperCase()}
                  </div>
                </div>
                
                {/* 用户名 */}
                <span className="flex-1 text-gray-700 text-sm font-medium truncate font-mono group-hover:text-orange-500 transition-colors">
                  {username}
                </span>
                
                {/* 外链图标 */}
                <svg 
                  className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                
                {/* 评论数 */}
                <div className="text-right flex-shrink-0">
                  <span className="text-gray-800 font-mono font-bold text-sm">
                    {count}
                  </span>
                  <span className="text-gray-400 text-xs ml-2">
                    ({(count / totalComments * 100).toFixed(1)}%)
                  </span>
                </div>
              </a>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ContributorsChart;
