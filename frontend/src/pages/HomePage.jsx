import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchProjects, getTopProjects } from '../api/github';
import { ErrorAlert, ErrorLogModal } from '../components/ErrorLogModal';
import HelpModal, { HelpIcon } from '../components/HelpModal';

// 搜索图标组件
const SearchIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

// OP Logo 组件 - 适合白色背景
const OPLogo = ({ size = 48 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    {/* 背景圆 - 渐变填充 */}
    <circle cx="50" cy="50" r="48" fill="url(#logoBgGradient)"/>
    
    {/* 外圈装饰 */}
    <circle cx="50" cy="50" r="44" stroke="rgba(255,255,255,0.3)" strokeWidth="2"/>
    
    {/* O - 左侧圆形 */}
    <circle cx="35" cy="50" r="16" stroke="white" strokeWidth="3.5" fill="none"/>
    {/* O 内部光点 */}
    <circle cx="35" cy="50" r="4" fill="white" opacity="0.9"/>
    
    {/* P - 右侧 */}
    <path d="M50 34 L50 66 M50 34 L63 34 C72 34 76 40 76 46 C76 52 72 58 63 58 L50 58" 
          stroke="white" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
    {/* P 内部装饰点 */}
    <circle cx="63" cy="46" r="3" fill="#22d3ee"/>
    
    {/* 脉冲动画线 */}
    <path d="M53 50 L58 50" stroke="rgba(255,255,255,0.8)" strokeWidth="2" strokeLinecap="round">
      <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>
    </path>
    
    {/* 渐变定义 */}
    <defs>
      <linearGradient id="logoBgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#7c3aed"/>
        <stop offset="50%" stopColor="#8b5cf6"/>
        <stop offset="100%" stopColor="#06b6d4"/>
      </linearGradient>
    </defs>
  </svg>
);

// 加载动画组件
const LoadingSpinner = () => (
  <div className="flex items-center justify-center py-12">
    <div className="relative">
      <div className="w-10 h-10 rounded-full border-2 border-gray-200"></div>
      <div className="absolute top-0 left-0 w-10 h-10 rounded-full border-2 border-transparent border-t-purple-500 animate-spin"></div>
    </div>
    <span className="ml-4 text-gray-500" style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>加载中...</span>
  </div>
);

// 活跃度排行榜 - 长方形卡片组件
const TopProjectCard = ({ project, rank, onClick }) => {
  const colorSchemes = {
    1: {
      bg: 'bg-gradient-to-r from-amber-50 to-orange-50',
      border: 'border-amber-200',
      badge: 'bg-amber-500',
      text: 'text-amber-700',
      label: '🥇 TOP 1'
    },
    2: {
      bg: 'bg-gradient-to-r from-slate-50 to-gray-100',
      border: 'border-gray-300',
      badge: 'bg-gray-500',
      text: 'text-gray-700',
      label: '🥈 TOP 2'
    },
    3: {
      bg: 'bg-gradient-to-r from-orange-50 to-amber-50',
      border: 'border-orange-200',
      badge: 'bg-orange-400',
      text: 'text-orange-700',
      label: '🥉 TOP 3'
    }
  };

  const scheme = colorSchemes[rank] || colorSchemes[3];

  return (
    <div 
      onClick={onClick}
      className={`relative cursor-pointer transform transition-all duration-300 hover:scale-[1.02] hover:shadow-lg
                  ${scheme.bg} ${scheme.border} border-2 rounded-xl p-5 w-full`}
    >
      {/* 排名徽章 */}
      <div className={`absolute -top-2 -left-2 ${scheme.badge} text-white text-xs font-bold 
                       px-3 py-1 rounded-full shadow-md`}>
        {scheme.label}
      </div>
      
      {/* 内容区域 */}
      <div className="pt-2">
        {/* 项目名称 */}
        <h3 className={`font-bold text-lg ${scheme.text} mb-1 truncate`}
            style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>
          {project.repo_name?.split('/')[1] || project.repo_name}
        </h3>
        
        {/* 组织名称 */}
        <p className="text-gray-500 text-sm mb-3 truncate">
          {project.repo_name?.split('/')[0]}
        </p>
        
        {/* 统计数据 */}
        <div className="flex items-center gap-4 text-sm">
          <span className="flex items-center gap-1.5">
            <span className="text-amber-500">⭐</span>
            <span className="font-semibold text-gray-700">
              {(project.stars / 1000).toFixed(1)}k
            </span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="text-cyan-600">🍴</span>
            <span className="font-semibold text-gray-700">
              {project.forks ? (project.forks / 1000).toFixed(1) + 'k' : '-'}
            </span>
          </span>
        </div>
      </div>
    </div>
  );
};

// 活跃度排行榜 - 轮播展示区域
const Top3Section = ({ projects, onProjectClick, isLoading, error, errorDetails }) => {
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  // 自动轮播 - 每2秒切换
  useEffect(() => {
    if (!projects || projects.length === 0) return;
    
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % projects.length);
    }, 2000);
    
    return () => clearInterval(timer);
  }, [projects]);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="w-64 h-32 rounded-xl bg-gray-100 animate-pulse border border-gray-200"></div>
          ))}
        </div>
      </div>
    );
  }

  // 数据加载失败时显示友好提示
  if (error || (!projects || projects.length === 0)) {
    const hasDetails = errorDetails && (errorDetails.traceback || errorDetails.error_type);
    
    return (
      <div className="relative py-8 mb-6">
        <h2 className="text-center text-xl font-semibold mb-6 text-gray-700 tracking-wide"
            style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>
          <span className="text-amber-500">🏆</span> 活跃度排行榜
        </h2>
        <div 
          className={`flex flex-col items-center justify-center py-8 px-4 rounded-xl bg-gray-50
                     ${hasDetails ? 'cursor-pointer hover:bg-red-50 transition-colors' : ''}`}
          onClick={() => hasDetails && setShowErrorModal(true)}
        >
          <div className="text-4xl mb-4 opacity-50">⚠️</div>
          <p className="text-gray-600 text-center mb-2">
            {error || '无法加载排行榜数据'}
          </p>
          <p className="text-gray-500 text-sm text-center">
            请确保数据库服务已启动，然后刷新页面
          </p>
          {hasDetails && (
            <p className="text-red-500/70 text-xs mt-3 flex items-center gap-1">
              <span>📋</span>
              点击查看详细错误日志
            </p>
          )}
        </div>
        
        {/* 错误日志弹窗 */}
        {hasDetails && (
          <ErrorLogModal 
            isOpen={showErrorModal} 
            onClose={() => setShowErrorModal(false)} 
            errorDetails={errorDetails} 
          />
        )}
      </div>
    );
  }

  return (
    <div className="relative py-8 mb-6">
      {/* 标题 */}
      <h2 className="text-center text-xl font-semibold mb-8 text-slate-700 tracking-wide"
          style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>
        <span className="text-amber-500">🏆</span> 活跃度排行榜
      </h2>
      
      {/* 轮播容器 */}
      <div className="activity-slider max-w-sm mx-auto">
        <div 
          className="activity-slider-track"
          style={{ transform: `translateX(-${currentIndex * 100}%)` }}
        >
          {projects.map((project, index) => (
            <div key={project.id || index} className="activity-slider-item px-2">
              <TopProjectCard
                project={project}
                rank={index + 1}
                onClick={() => onProjectClick(project)}
              />
            </div>
          ))}
        </div>
      </div>
      
      {/* 轮播指示器 */}
      <div className="flex justify-center gap-2 mt-6">
        {projects.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentIndex(index)}
            className={`slider-dot ${index === currentIndex ? 'active' : ''}`}
            aria-label={`切换到第 ${index + 1} 个项目`}
          />
        ))}
      </div>
    </div>
  );
};

// 项目卡片组件 - 浅色风格
const ProjectCard = ({ project, onClick }) => (
  <div
    onClick={onClick}
    className="p-5 rounded-xl cursor-pointer transition-all duration-300
              bg-white border border-gray-200 
              hover:bg-gray-50 hover:border-purple-300 
              hover:shadow-lg hover:shadow-purple-100 hover:-translate-y-1"
    style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}
  >
    <div className="flex items-center justify-between mb-3">
      <h3 className="font-semibold text-gray-800 text-base truncate pr-2">{project.repo_name}</h3>
      <span className="text-gray-400 text-sm group-hover:text-purple-500">→</span>
    </div>
    <div className="flex gap-5 text-sm text-gray-600">
      <span className="flex items-center gap-1.5">
        <span className="text-amber-500">⭐</span>
        <span className="text-amber-600 font-medium">{project.stars?.toLocaleString() || 0}</span>
      </span>
      <span className="flex items-center gap-1.5">
        <span className="text-cyan-600">🍴</span>
        <span className="text-cyan-700 font-medium">{project.forks?.toLocaleString() || 0}</span>
      </span>
    </div>
    {project.updated_at && (
      <p className="text-xs text-gray-500 mt-3">
        更新于 {project.updated_at}
      </p>
    )}
  </div>
);

const HomePage = () => {
  const navigate = useNavigate();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);
  const [errorDetails, setErrorDetails] = useState(null); // 存储详细错误信息
  const [topProjects, setTopProjects] = useState([]);
  const [isLoadingTop, setIsLoadingTop] = useState(true);
  const [topError, setTopError] = useState(null);
  const [topErrorDetails, setTopErrorDetails] = useState(null); // Top项目错误详情
  const [showHelpModal, setShowHelpModal] = useState(false); // 帮助弹窗状态

  // 防抖搜索
  const [debouncedKeyword, setDebouncedKeyword] = useState('');

  // 加载Top 3项目
  useEffect(() => {
    const fetchTopProjects = async () => {
      setIsLoadingTop(true);
      setTopError(null);
      setTopErrorDetails(null);
      try {
        const result = await getTopProjects(3);
        if (!result.items || result.items.length === 0) {
          setTopError('数据库连接失败或暂无数据');
        }
        setTopProjects(result.items || []);
      } catch (err) {
        console.error('获取Top项目失败:', err);
        setTopError(err.message || '无法连接到服务器，请检查后端服务');
        // 存储详细错误信息
        if (err.details) {
          setTopErrorDetails(err.details);
        }
      } finally {
        setIsLoadingTop(false);
      }
    };
    fetchTopProjects();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedKeyword(searchKeyword);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchKeyword]);

  // 搜索项目
  const handleSearch = useCallback(async () => {
    if (!debouncedKeyword.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    setError(null);
    setErrorDetails(null);

    try {
      const result = await searchProjects({
        keyword: debouncedKeyword,
        limit: 50
      });
      setSearchResults(result.items || []);
    } catch (err) {
      console.error('搜索失败:', err);
      setError(err.message || '搜索失败，请确保后端服务已启动');
      // 存储详细错误信息
      if (err.details) {
        setErrorDetails(err.details);
      }
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, [debouncedKeyword]);

  // 当关键词变化时触发搜索
  useEffect(() => {
    handleSearch();
  }, [debouncedKeyword, handleSearch]);

  // 点击项目跳转详情页
  const handleProjectClick = (project) => {
    const projectKey = project.project_key || project.repo_name.replace('/', '_');
    navigate(`/project/${encodeURIComponent(projectKey)}`);
  };

  return (
    <div className="min-h-screen grid-bg">
      {/* 右上角帮助按钮 */}
      <button
        onClick={() => setShowHelpModal(true)}
        className="fixed top-4 right-4 z-40 p-3 rounded-xl 
                   bg-white/90 backdrop-blur-sm border border-gray-200
                   text-gray-500 hover:text-purple-600 hover:border-purple-300
                   transition-all duration-300 group shadow-sm"
        title="帮助文档"
      >
        <HelpIcon />
        <span className="absolute right-full mr-2 top-1/2 -translate-y-1/2 px-2 py-1 
                        bg-gray-800 text-xs text-gray-100 rounded whitespace-nowrap
                        opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          使用帮助
        </span>
      </button>

      {/* 帮助弹窗 */}
      <HelpModal isOpen={showHelpModal} onClose={() => setShowHelpModal(false)} />

      {/* 顶部 Hero 区域 */}
      <div className="relative overflow-hidden">
        {/* 顶部装饰线 */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-300/40 to-transparent"></div>
        
        <div className="max-w-4xl mx-auto px-6 py-14 text-center relative">
          {/* OP Logo */}
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <OPLogo size={72} />
            </div>
          </div>
          
          {/* 标题 */}
          <h1 className="text-5xl font-bold mb-3 tracking-tight">
            <span className="bg-gradient-to-r from-slate-800 via-slate-700 to-slate-600 bg-clip-text text-transparent"
                  style={{ fontFamily: '"Noto Sans SC", "PingFang SC", sans-serif' }}>
              OpenPulse
            </span>
          </h1>
          <p className="text-lg text-slate-500 mb-10" style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>
            探索开源项目数据，发现社区趋势
          </p>

          {/* 大搜索框 - 浅色风格 */}
          <div className="relative max-w-2xl mx-auto">
            <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none text-gray-400">
              <SearchIcon />
            </div>
            <input
              type="text"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              placeholder="搜索项目 (例如: react, vue, tensorflow...)"
              className="w-full pl-14 pr-6 py-4 bg-white border border-gray-200 rounded-xl 
                       text-gray-800 text-lg placeholder-gray-400
                       focus:outline-none focus:border-purple-400 focus:ring-2 focus:ring-purple-100
                       transition-all duration-300 shadow-sm"
              style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}
            />
            {isSearching && (
              <div className="absolute inset-y-0 right-0 pr-5 flex items-center">
                <div className="w-5 h-5 border-2 border-purple-200 border-t-purple-500 rounded-full animate-spin"></div>
              </div>
            )}
          </div>

          {/* 快捷标签 */}
          <div className="flex flex-wrap justify-center gap-2 mt-5">
            {['react', 'vue', 'tensorflow', 'pytorch', 'rust'].map(tag => (
              <button
                key={tag}
                onClick={() => setSearchKeyword(tag)}
                className="px-4 py-1.5 bg-gray-100 border border-gray-200 rounded-full text-sm text-gray-600 
                         hover:bg-purple-50 hover:text-purple-700 hover:border-purple-300 transition-all"
              >
                {tag}
              </button>
            ))}
          </div>

          {/* Top 3 项目展示 */}
          <Top3Section 
            projects={topProjects} 
            onProjectClick={handleProjectClick}
            isLoading={isLoadingTop}
            error={topError}
            errorDetails={topErrorDetails}
          />
        </div>
      </div>

      {/* 分隔线 */}
      <div className="max-w-4xl mx-auto px-6">
        <div className="h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
      </div>

      {/* 搜索结果 */}
      <main className="max-w-6xl mx-auto px-6 py-8 pb-12">
        {/* 错误提示 - 点击可查看详细日志 */}
        {error && (
          <ErrorAlert 
            message={error} 
            errorDetails={errorDetails}
            className="mb-6"
          />
        )}

        {/* 搜索提示 */}
        {!searchKeyword && searchResults.length === 0 && (
          <div className="text-center py-16">
            <div className="text-5xl mb-6 opacity-40">🔍</div>
            <p className="text-slate-600 text-lg" style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>输入关键词搜索开源项目</p>
            <p className="text-slate-400 mt-2" style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>
              支持搜索 Star 数 Top 300 的热门项目
            </p>
          </div>
        )}

        {/* 搜索中 */}
        {isSearching && <LoadingSpinner />}

        {/* 无结果 */}
        {!isSearching && searchKeyword && searchResults.length === 0 && (
          <div className="text-center py-16">
            <div className="text-5xl mb-6 opacity-40">📭</div>
            <p className="text-slate-600 text-lg" style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>未找到相关项目</p>
            <p className="text-slate-400 mt-2" style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>试试其他关键词</p>
          </div>
        )}

        {/* 结果网格 */}
        {!isSearching && searchResults.length > 0 && (
          <>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-700" style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>
                搜索结果
                <span className="text-slate-400 font-normal ml-3 text-base">
                  ({searchResults.length} 个项目)
                </span>
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map((project, index) => (
                <ProjectCard
                  key={project.id || index}
                  project={project}
                  onClick={() => handleProjectClick(project)}
                />
              ))}
            </div>
          </>
        )}
      </main>

      {/* 底部 */}
      <footer className="py-8 border-t border-slate-200">
        <div className="max-w-6xl mx-auto px-6 text-center text-slate-400 text-sm" style={{ fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif" }}>
          <p>OpenPulse - 开源项目数据分析平台</p>
          <p className="mt-1">基于 GitHub 开源数据构建</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
