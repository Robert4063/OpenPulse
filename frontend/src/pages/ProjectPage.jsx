import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TrendChart from '../components/TrendChart';
import ContributorsChart from '../components/ContributorsChart';
import HealthScore from '../components/HealthScore';
import { ErrorAlert } from '../components/ErrorLogModal';
import { getProjectTrends, getContributors, getHealthScore } from '../api/github';

// 返回图标
const BackIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
  </svg>
);

// OP Logo 小版本 - 适合白色背景
const OPLogoSmall = () => (
  <svg width="32" height="32" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    {/* 背景圆 - 渐变填充 */}
    <circle cx="50" cy="50" r="48" fill="url(#logoSmallBgGradient)"/>
    {/* 外圈装饰 */}
    <circle cx="50" cy="50" r="44" stroke="rgba(255,255,255,0.3)" strokeWidth="2"/>
    {/* O */}
    <circle cx="35" cy="50" r="16" stroke="white" strokeWidth="3" fill="none"/>
    <circle cx="35" cy="50" r="4" fill="white" opacity="0.9"/>
    {/* P */}
    <path d="M50 34 L50 66 M50 34 L63 34 C72 34 76 40 76 46 C76 52 72 58 63 58 L50 58" 
          stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
    <circle cx="63" cy="46" r="2.5" fill="#22d3ee"/>
    <defs>
      <linearGradient id="logoSmallBgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#f97316"/>
        <stop offset="50%" stopColor="#fb923c"/>
        <stop offset="100%" stopColor="#fbbf24"/>
      </linearGradient>
    </defs>
  </svg>
);

// 加载动画组件
const LoadingSpinner = ({ text = '加载中...' }) => (
  <div className="flex items-center justify-center py-12">
    <div className="relative">
      <div className="w-10 h-10 rounded-full border-2 border-gray-200"></div>
      <div className="absolute top-0 left-0 w-10 h-10 rounded-full border-2 border-transparent border-t-orange-500 animate-spin"></div>
    </div>
    <span className="ml-4 text-gray-500">{text}</span>
  </div>
);

// 项目摘要卡片
const SummaryCard = ({ icon, label, value, color }) => (
  <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
    <div className="flex items-center gap-3 mb-2">
      <span className="text-xl">{icon}</span>
      <span className="text-gray-500 text-sm">{label}</span>
    </div>
    <p className={`text-3xl font-bold ${color}`}>
      {typeof value === 'number' ? value.toLocaleString() : value || '-'}
    </p>
  </div>
);

const ProjectPage = () => {
  const { projectKey } = useParams();
  const navigate = useNavigate();
  
  const [projectTrends, setProjectTrends] = useState(null);
  const [contributorsData, setContributorsData] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [isLoadingTrends, setIsLoadingTrends] = useState(true);
  const [isLoadingContributors, setIsLoadingContributors] = useState(true);
  const [isLoadingHealth, setIsLoadingHealth] = useState(true);
  const [error, setError] = useState(null);
  const [errorDetails, setErrorDetails] = useState(null); // 存储详细错误信息
  const [loadingProgress, setLoadingProgress] = useState(0);

  // 将 project_key 转换为显示名称 (owner_repo -> owner/repo)
  const displayName = projectKey ? decodeURIComponent(projectKey).replace('_', '/') : '';

  useEffect(() => {
    if (!projectKey) return;

    const decodedKey = decodeURIComponent(projectKey);
    let completedCount = 0;
    const totalRequests = 3;
    
    const updateProgress = () => {
      completedCount++;
      setLoadingProgress(Math.round((completedCount / totalRequests) * 100));
    };

    // 重置状态
    setProjectTrends(null);
    setContributorsData(null);
    setHealthData(null);
    setError(null);
    setErrorDetails(null);
    setLoadingProgress(0);
    setIsLoadingTrends(true);
    setIsLoadingContributors(true);
    setIsLoadingHealth(true);

    // 并行加载所有数据，使用 Promise.allSettled 确保即使有请求失败也不影响其他请求
    const loadTrends = getProjectTrends(decodedKey)
      .then(data => {
        setProjectTrends(data);
        updateProgress();
      })
      .catch(err => {
        console.error('加载趋势数据失败:', err);
        setError(err.message || '加载趋势数据失败');
        // 存储详细错误信息
        if (err.details) {
          setErrorDetails(err.details);
        }
        updateProgress();
      })
      .finally(() => {
        setIsLoadingTrends(false);
      });

    const loadContributors = getContributors(decodedKey, 10)
      .then(data => {
        setContributorsData(data);
        updateProgress();
      })
      .catch(err => {
        console.error('加载贡献者数据失败:', err);
        // 如果还没有错误，设置这个错误
        if (!error) {
          setError(err.message || '加载贡献者数据失败');
          if (err.details) {
            setErrorDetails(err.details);
          }
        }
        updateProgress();
      })
      .finally(() => {
        setIsLoadingContributors(false);
      });

    const loadHealth = getHealthScore(decodedKey)
      .then(data => {
        setHealthData(data);
        updateProgress();
      })
      .catch(err => {
        console.error('加载健康度数据失败:', err);
        // 如果还没有错误，设置这个错误
        if (!error) {
          setError(err.message || '加载健康度数据失败');
          if (err.details) {
            setErrorDetails(err.details);
          }
        }
        updateProgress();
      })
      .finally(() => {
        setIsLoadingHealth(false);
      });

    // 等待所有请求完成
    Promise.allSettled([loadTrends, loadContributors, loadHealth]);
  }, [projectKey]);

  // 检查是否正在加载
  const isAnyLoading = isLoadingTrends || isLoadingContributors || isLoadingHealth;

  return (
    <div className="min-h-screen grid-bg">
      {/* 顶部加载进度条 */}
      {isAnyLoading && (
        <div className="fixed top-0 left-0 right-0 z-[100] h-1 bg-gray-200">
          <div 
            className="h-full bg-gradient-to-r from-orange-400 via-orange-500 to-orange-400 transition-all duration-300 ease-out"
            style={{ 
              width: `${loadingProgress}%`,
              boxShadow: '0 0 10px rgba(249, 115, 22, 0.5)'
            }}
          />
        </div>
      )}

      {/* 顶部导航栏 */}
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            {/* 返回按钮 + Logo */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="p-2 rounded-lg bg-gray-50 border border-gray-200 text-gray-500 
                         hover:text-gray-700 hover:border-orange-300 transition-all"
              >
                <BackIcon />
              </button>
              <div className="flex items-center gap-3">
                <OPLogoSmall />
                <div>
                  <h1 className="text-lg font-bold bg-gradient-to-r from-slate-800 via-slate-700 to-slate-600 bg-clip-text text-transparent">
                    OpenPulse
                  </h1>
                  <p className="text-xs text-slate-400">项目详情</p>
                </div>
              </div>
            </div>

            {/* GitHub链接 */}
            <a
              href={`https://github.com/${displayName}`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-600 
                       hover:bg-orange-50 hover:border-orange-300 transition-all flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
              </svg>
              在 GitHub 查看
            </a>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* 错误提示 - 点击可查看详细日志 */}
        {error && (
          <ErrorAlert 
            message={error} 
            errorDetails={errorDetails}
            className="mb-6"
          />
        )}

        {/* 项目标题 */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 mb-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-700">
            {displayName}
          </h2>
          <p className="text-slate-400 mt-2">项目趋势数据分析</p>
        </div>

        {/* 数据摘要 */}
        {isLoadingTrends ? (
          <div className="grid grid-cols-2 gap-4 mb-6">
            {[1, 2].map(i => (
              <div key={i} className="bg-white rounded-xl p-5 border border-gray-200 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-20 mb-3"></div>
                <div className="h-8 bg-gray-200 rounded w-24"></div>
              </div>
            ))}
          </div>
        ) : projectTrends?.summary && (
          <div className="grid grid-cols-2 gap-4 mb-6">
            <SummaryCard
              icon="⭐"
              label="总 Stars"
              value={projectTrends.summary.total_stars}
              color="text-orange-500"
            />
            <SummaryCard
              icon="🍴"
              label="总 Forks"
              value={projectTrends.summary.total_forks}
              color="text-amber-600"
            />
          </div>
        )}

        {/* 健康度评估 */}
        <div className="mb-6">
          <HealthScore 
            data={healthData} 
            isLoading={isLoadingHealth} 
            projectName={projectKey ? decodeURIComponent(projectKey) : null}
          />
        </div>

        {/* 趋势图表 */}
        {isLoadingTrends ? (
          <LoadingSpinner text="加载趋势数据..." />
        ) : projectTrends && (
          <div className="space-y-6">
            <TrendChart
              data={projectTrends.stars_trend}
              title="Stars 趋势"
              dailyColor="#fbbf24"
              totalColor="#f59e0b"
              icon="⭐"
              dailyLabel="每日新增 Stars"
              totalLabel="累计 Stars"
            />
            <TrendChart
              data={projectTrends.forks_trend}
              title="Forks 趋势"
              dailyColor="#22d3ee"
              totalColor="#06b6d4"
              icon="🍴"
              dailyLabel="每日新增 Forks"
              totalLabel="累计 Forks"
            />
          </div>
        )}

        {/* 活跃贡献者统计 */}
        <div className="mt-6">
          {isLoadingContributors ? (
            <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-2xl">👥</span>
                <h3 className="text-lg font-semibold text-slate-600">活跃贡献者</h3>
              </div>
              <LoadingSpinner text="加载活跃贡献者数据..." />
            </div>
          ) : contributorsData && (
            <ContributorsChart
              data={contributorsData}
              totalContributors={contributorsData.total_contributors || 0}
              totalCommits={contributorsData.total_commits || contributorsData.total_comments || 0}
            />
          )}
        </div>

        {/* 无数据提示 */}
        {!isLoadingTrends && !projectTrends && !error && (
          <div className="bg-white rounded-2xl p-12 border border-gray-200 text-center shadow-sm">
            <div className="text-5xl mb-4 opacity-30">📊</div>
            <p className="text-gray-500">暂无趋势数据</p>
          </div>
        )}
      </main>

      {/* 底部 */}
      <footer className="mt-12 py-8 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-6 text-center text-slate-400 text-sm">
          <p>OpenPulse - 开源项目数据分析平台</p>
          <p className="mt-1">基于 GitHub 开源数据构建</p>
        </div>
      </footer>
    </div>
  );
};

export default ProjectPage;
