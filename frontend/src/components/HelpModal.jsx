import React, { useState, useEffect } from 'react';

// 关闭图标
const CloseIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

// 帮助图标
export const HelpIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

// Tab 组件
const TabButton = ({ active, onClick, children }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200
               ${active 
                 ? 'bg-slate-100 text-slate-700 border border-slate-300' 
                 : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'}`}
  >
    {children}
  </button>
);

// 使用说明内容
const UsageGuide = () => (
  <div className="space-y-6 text-slate-600">
    <section>
      <h3 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <span className="text-orange-500">📊</span> 项目简介
      </h3>
      <p className="text-slate-500 leading-relaxed">
        <strong className="text-slate-700">OpenPulse</strong> 是一个开源项目数据分析平台，通过可视化展示 GitHub 项目的 Star、Fork、Watch、Issue、Comment 等数据趋势，帮助开发者了解开源项目的发展状况。
      </p>
    </section>

    <section>
      <h3 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <span className="text-amber-500">🔍</span> 如何使用
      </h3>
      <div className="space-y-3">
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <h4 className="font-medium text-slate-700 mb-2">1. 搜索项目</h4>
          <p className="text-slate-500 text-sm">在搜索框中输入项目关键词（如 react, vue, tensorflow），系统将自动搜索匹配的开源项目。</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <h4 className="font-medium text-slate-700 mb-2">2. 查看排行榜</h4>
          <p className="text-slate-500 text-sm">首页展示 Star 数量 Top 3 的热门项目，点击可查看详情。</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <h4 className="font-medium text-slate-700 mb-2">3. 项目详情</h4>
          <p className="text-slate-500 text-sm">点击任意项目卡片，进入详情页查看：</p>
          <ul className="text-slate-500 text-sm mt-2 space-y-1 ml-4">
            <li>• Star / Fork / Watch 趋势图表</li>
            <li>• 项目健康度评分</li>
            <li>• 贡献者分布分析</li>
            <li>• 相似项目推荐</li>
          </ul>
        </div>
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <h4 className="font-medium text-slate-700 mb-2">4. AI 助手</h4>
          <p className="text-slate-500 text-sm">点击右下角的 AI 助手图标，可以获得智能问答帮助。</p>
        </div>
      </div>
    </section>

    <section>
      <h3 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <span className="text-cyan-600">📁</span> 数据来源
      </h3>
      <p className="text-slate-500 leading-relaxed">
        数据通过 GitHub API 爬取，包含 <strong className="text-orange-500">Top 300</strong> 开源项目的 Star/Fork/Watch 历史数据、Issue 及评论数据。
        时间范围：2022-03 至 2023-03。
      </p>
    </section>
  </div>
);

// 健康度评价方法内容
const HealthScoreGuide = () => (
  <div className="space-y-6 text-slate-600">
    <section>
      <h3 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <span className="text-green-500">💚</span> 健康度评估模型 (PHAM v2.0)
      </h3>
      <p className="text-slate-500 leading-relaxed">
        本平台使用 <strong className="text-slate-700">Project Health Assessment Model</strong> 评估开源项目的健康程度。
        该算法基于四个维度进行加权评分，最终输出一个 <strong className="text-orange-500">0 ~ 100 分</strong> 的健康度数值。
      </p>
    </section>

    {/* 公式总览 */}
    <section className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-xl p-4 border border-slate-200">
      <h4 className="font-semibold text-slate-700 mb-3">📊 最终评分公式</h4>
      <div className="font-mono text-sm text-center py-3 bg-white rounded-lg text-slate-600 border border-slate-200">
        M = 0.2×Growth + 0.4×Activity + 0.2×Contrib + 0.2×Code
      </div>
    </section>

    {/* 四个维度详解 */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Growth */}
      <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
        <h4 className="font-medium text-amber-600 mb-2 flex items-center gap-2">
          <span>⭐</span> 关注度增长 (20%)
        </h4>
        <p className="text-slate-500 text-sm mb-2">计算 Star 和 Fork 相对于前三个月的增长率</p>
        <div className="font-mono text-xs bg-white rounded p-2 text-slate-600 border border-amber-100">
          Score_x = min(Sᶜᵘʳ/(Sₐᵥₘ+1)×100, 200) / 2
        </div>
        <p className="text-slate-400 text-xs mt-2">增长率上限 200%，防止小项目分数爆炸</p>
      </div>

      {/* Activity */}
      <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
        <h4 className="font-medium text-orange-600 mb-2 flex items-center gap-2">
          <span>🔥</span> 活跃度 (40%)
        </h4>
        <p className="text-slate-500 text-sm mb-2">结合 Commit 趋势和 OpenDigger 活跃度</p>
        <div className="font-mono text-xs bg-white rounded p-2 text-slate-600 border border-orange-100">
          Score_z = 50 + (Ratio_z − 1) × 50
        </div>
        <p className="text-slate-400 text-xs mt-2">基准分 50，根据最近一周活跃度浮动</p>
      </div>

      {/* Contribution */}
      <div className="bg-cyan-50 rounded-lg p-4 border border-cyan-200">
        <h4 className="font-medium text-cyan-600 mb-2 flex items-center gap-2">
          <span>🤝</span> 贡献度 (20%)
        </h4>
        <p className="text-slate-500 text-sm mb-2">通过 PR 趋势判断社区贡献热度</p>
        <div className="font-mono text-xs bg-white rounded p-2 text-slate-600 border border-cyan-100">
          Ratio_n = (Pₗₐₛₜ+1) / (Pₘₒₙₜₕ+1)
        </div>
        <p className="text-slate-400 text-xs mt-2">计算 PR 的近期变化趋势</p>
      </div>

      {/* Code Churn */}
      <div className="bg-green-50 rounded-lg p-4 border border-green-200">
        <h4 className="font-medium text-green-600 mb-2 flex items-center gap-2">
          <span>💻</span> 代码健康度 (20%)
        </h4>
        <p className="text-slate-500 text-sm mb-2">使用代码变动总量衡量开发吞吐量</p>
        <div className="font-mono text-xs bg-white rounded p-2 text-slate-600 border border-green-100">
          Score_Code = min(100, 20×log₁₀(q+1))
        </div>
        <p className="text-slate-400 text-xs mt-2">对数函数平滑处理，边际效应递减</p>
      </div>
    </div>

    {/* 数据指标说明 */}
    <section>
      <h3 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <span className="text-blue-500">📋</span> 输入数据指标
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-200">
              <th className="py-2 px-3">维度</th>
              <th className="py-2 px-3">指标</th>
              <th className="py-2 px-3">说明</th>
            </tr>
          </thead>
          <tbody className="text-slate-600">
            <tr className="border-b border-slate-100">
              <td className="py-2 px-3 text-amber-600">Star</td>
              <td className="py-2 px-3">star_current_month</td>
              <td className="py-2 px-3">本月新增 Star 数</td>
            </tr>
            <tr className="border-b border-slate-100">
              <td className="py-2 px-3 text-amber-600">Fork</td>
              <td className="py-2 px-3">fork_current_month</td>
              <td className="py-2 px-3">本月新增 Fork 数</td>
            </tr>
            <tr className="border-b border-slate-100">
              <td className="py-2 px-3 text-orange-600">Commit</td>
              <td className="py-2 px-3">commit_avg_last_week</td>
              <td className="py-2 px-3">最后一周平均 Commit 数</td>
            </tr>
            <tr className="border-b border-slate-100">
              <td className="py-2 px-3 text-orange-600">Activity</td>
              <td className="py-2 px-3">opendigger_activity</td>
              <td className="py-2 px-3">OpenDigger 活跃度指标</td>
            </tr>
            <tr className="border-b border-slate-100">
              <td className="py-2 px-3 text-cyan-600">PR</td>
              <td className="py-2 px-3">pr_avg_last_week</td>
              <td className="py-2 px-3">最后一周平均 PR 数</td>
            </tr>
            <tr>
              <td className="py-2 px-3 text-green-600">Code</td>
              <td className="py-2 px-3">pull_additions/deletions</td>
              <td className="py-2 px-3">代码添加/删除行数</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    {/* 分数参考 */}
    <section className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-xl p-4 border border-slate-200">
      <h4 className="font-semibold text-slate-700 mb-3">📈 分数参考</h4>
      <div className="grid grid-cols-4 gap-2 text-center text-sm">
        <div className="bg-red-50 rounded-lg p-2 border border-red-200">
          <div className="text-red-500 font-bold">0-40</div>
          <div className="text-slate-400 text-xs">需关注</div>
        </div>
        <div className="bg-amber-50 rounded-lg p-2 border border-amber-200">
          <div className="text-amber-500 font-bold">40-60</div>
          <div className="text-slate-400 text-xs">一般</div>
        </div>
        <div className="bg-green-50 rounded-lg p-2 border border-green-200">
          <div className="text-green-500 font-bold">60-80</div>
          <div className="text-slate-400 text-xs">良好</div>
        </div>
        <div className="bg-cyan-50 rounded-lg p-2 border border-cyan-200">
          <div className="text-cyan-500 font-bold">80-100</div>
          <div className="text-slate-400 text-xs">优秀</div>
        </div>
      </div>
    </section>
  </div>
);

// 主模态框组件
const HelpModal = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('usage');

  // 按 ESC 关闭
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* 模态框内容 */}
      <div className="relative w-full max-w-3xl max-h-[85vh] bg-white rounded-2xl border border-slate-200 shadow-2xl overflow-hidden animate-fade-in">
        {/* 头部 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-100 to-amber-100 flex items-center justify-center">
              <span className="text-xl">📖</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-700">帮助文档</h2>
              <p className="text-sm text-slate-400">OpenPulse 使用指南</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <CloseIcon />
          </button>
        </div>

        {/* Tab 切换 */}
        <div className="flex gap-2 px-6 py-3 border-b border-slate-100">
          <TabButton 
            active={activeTab === 'usage'} 
            onClick={() => setActiveTab('usage')}
          >
            📘 使用说明
          </TabButton>
          <TabButton 
            active={activeTab === 'health'} 
            onClick={() => setActiveTab('health')}
          >
            💚 健康度评价
          </TabButton>
        </div>

        {/* 内容区域 */}
        <div className="p-6 overflow-y-auto max-h-[calc(85vh-140px)] custom-scrollbar">
          {activeTab === 'usage' ? <UsageGuide /> : <HealthScoreGuide />}
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(-10px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
        .animate-fade-in {
          animation: fade-in 0.2s ease-out;
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
    </div>
  );
};

export default HelpModal;
