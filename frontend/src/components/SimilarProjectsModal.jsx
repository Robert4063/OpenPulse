import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSimilarProjects, getProjectLanguages } from '../api/github';

// 关闭图标
const CloseIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
  </svg>
);

/**
 * 相似项目模态框 - 棱角线条风格
 */
const SimilarProjectsModal = ({ isOpen, onClose, projectName, currentScore, currentGrade }) => {
  const navigate = useNavigate();
  const [similarProjects, setSimilarProjects] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('similar'); // 'similar' | 'languages'

  useEffect(() => {
    if (isOpen && projectName) {
      fetchData();
    }
  }, [isOpen, projectName]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [similarData, langData] = await Promise.all([
        getSimilarProjects(projectName, 5),
        getProjectLanguages(projectName)
      ]);
      
      setSimilarProjects(similarData.similar_projects || []);
      setLanguages(langData.languages || []);
    } catch (err) {
      console.error('获取数据失败:', err);
      setError(err.message || '获取数据失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProjectClick = (project) => {
    const projectKey = project.project_key || project.project?.replace('/', '_');
    if (projectKey) {
      onClose();
      navigate(`/project/${encodeURIComponent(projectKey)}`);
    }
  };

  const getGradeColor = (grade) => {
    const colors = {
      'S': '#fbbf24',
      'A': '#a855f7',
      'B': '#3b82f6',
      'C': '#22c55e',
      'D': '#6b7280'
    };
    return colors[grade] || '#6b7280';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* 弹窗内容 */}
      <div className="relative bg-[#0a0a12] border border-gray-700 w-full max-w-2xl max-h-[80vh] overflow-hidden">
        {/* 角标装饰 */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-purple-500" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-purple-500" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-purple-500" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-purple-500" />
        
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-1 h-6 bg-purple-500" />
            <div>
              <h3 className="text-gray-200 uppercase tracking-widest text-sm font-medium">
                PROJECT ANALYSIS
              </h3>
              <p className="text-gray-600 text-xs mt-0.5 font-mono">{projectName}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 text-gray-400 hover:text-gray-200 transition-colors"
          >
            <CloseIcon />
          </button>
        </div>

        {/* Tab 切换 */}
        <div className="flex border-b border-gray-800">
          <button
            onClick={() => setActiveTab('similar')}
            className={`flex-1 px-4 py-3 text-sm font-medium uppercase tracking-widest transition-colors ${
              activeTab === 'similar'
                ? 'text-purple-400 border-b-2 border-purple-500 bg-purple-500/5'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            相似项目
          </button>
          <button
            onClick={() => setActiveTab('languages')}
            className={`flex-1 px-4 py-3 text-sm font-medium uppercase tracking-widest transition-colors ${
              activeTab === 'languages'
                ? 'text-cyan-400 border-b-2 border-cyan-500 bg-cyan-500/5'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            技术栈
          </button>
        </div>
        
        {/* 内容区 */}
        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-2 border-gray-700 border-t-purple-500 animate-spin" />
              <span className="ml-3 text-gray-400 text-sm uppercase tracking-wider">Loading...</span>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          ) : activeTab === 'similar' ? (
            /* 相似项目列表 */
            <div className="space-y-2">
              {similarProjects.length === 0 ? (
                <div className="text-center py-8 text-gray-600 text-sm uppercase tracking-wider">
                  NO SIMILAR PROJECTS
                </div>
              ) : (
                similarProjects.map((project, index) => (
                  <div
                    key={index}
                    onClick={() => handleProjectClick(project)}
                    className="p-4 bg-gray-900/30 border border-gray-800 hover:border-purple-500/50 
                             cursor-pointer transition-all group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-gray-600 font-mono text-sm">#{index + 1}</span>
                        <div>
                          <h4 className="text-gray-200 font-medium font-mono group-hover:text-purple-400 transition-colors">
                            {project.project?.replace('_', '/') || project.project_key?.replace('_', '/')}
                          </h4>
                          <p className="text-gray-500 text-xs mt-1">
                            相似度: <span className="text-cyan-400 font-mono">{(project.similarity * 100).toFixed(1)}%</span>
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-gray-600 text-[10px] uppercase tracking-wider">Score</p>
                          <p className="font-mono font-bold text-lg" style={{ color: getGradeColor(project.grade) }}>
                            {project.final_score?.toFixed(0) || '-'}
                          </p>
                        </div>
                        <div 
                          className="w-10 h-10 flex items-center justify-center border-2 font-mono text-xl font-bold"
                          style={{ borderColor: getGradeColor(project.grade), color: getGradeColor(project.grade) }}
                        >
                          {project.grade || '-'}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          ) : (
            /* 技术栈分布 */
            <div className="space-y-3">
              {languages.length === 0 ? (
                <div className="text-center py-8 text-gray-600 text-sm uppercase tracking-wider">
                  NO LANGUAGE DATA
                </div>
              ) : (
                languages.map((lang, index) => (
                  <div key={index} className="group">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-2 h-2"
                          style={{ backgroundColor: lang.color || '#6b7280' }}
                        />
                        <span className="text-gray-300 text-sm font-mono">{lang.name}</span>
                      </div>
                      <span className="text-gray-500 text-xs font-mono">{lang.percentage?.toFixed(1)}%</span>
                    </div>
                    <div className="h-1 bg-gray-800 relative">
                      <div
                        className="h-full transition-all duration-500"
                        style={{
                          width: `${lang.percentage || 0}%`,
                          backgroundColor: lang.color || '#6b7280'
                        }}
                      />
                      {/* 刻度线 */}
                      <div className="absolute inset-0 flex">
                        {[25, 50, 75].map(mark => (
                          <div 
                            key={mark}
                            className="absolute top-0 w-px h-full bg-gray-700"
                            style={{ left: `${mark}%` }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* 底部信息 */}
        <div className="px-4 py-3 border-t border-gray-800 bg-gray-900/30">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <span className="uppercase tracking-wider">
              {activeTab === 'similar' ? `${similarProjects.length} SIMILAR` : `${languages.length} LANGUAGES`}
            </span>
            <div className="flex items-center gap-4">
              <span>当前评分: <span className="text-white font-mono">{currentScore?.toFixed(0) || '-'}</span></span>
              <span 
                className="font-mono font-bold px-2 py-0.5 border"
                style={{ borderColor: getGradeColor(currentGrade), color: getGradeColor(currentGrade) }}
              >
                {currentGrade || '-'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimilarProjectsModal;
