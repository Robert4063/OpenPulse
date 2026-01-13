import React, { useState } from 'react';

/**
 * 错误日志弹窗组件
 * 用于显示详细的错误信息，包括traceback
 */
export const ErrorLogModal = ({ isOpen, onClose, errorDetails }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !errorDetails) return null;

  const handleCopy = () => {
    const errorText = `
错误类型: ${errorDetails.error_type || 'Unknown'}
错误信息: ${errorDetails.error || errorDetails.message || 'Unknown'}
时间: ${new Date().toLocaleString('zh-CN')}

Traceback:
${errorDetails.traceback || 'No traceback available'}
    `.trim();

    navigator.clipboard.writeText(errorText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* 弹窗内容 */}
      <div className="relative bg-[#0f0f0f] border border-red-500/30 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl shadow-red-500/10">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center">
              <span className="text-red-400">⚠️</span>
            </div>
            <div>
              <h3 className="text-red-400 font-semibold">错误日志</h3>
              <p className="text-gray-500 text-xs">Error Details</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-gray-200 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* 内容区 */}
        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {/* 错误类型和消息 */}
          <div className="mb-4 p-3 bg-red-500/10 rounded-lg border border-red-500/20">
            <div className="flex items-start gap-2 mb-2">
              <span className="text-red-400 text-xs font-mono bg-red-500/20 px-1.5 py-0.5 rounded">
                {errorDetails.error_type || 'Error'}
              </span>
            </div>
            <p className="text-red-300 text-sm">
              {errorDetails.error || errorDetails.message || 'Unknown error'}
            </p>
          </div>
          
          {/* Traceback */}
          {errorDetails.traceback && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Traceback</h4>
              </div>
              <pre className="bg-[#0a0a0a] border border-gray-800 rounded-lg p-3 text-xs text-gray-300 font-mono overflow-x-auto whitespace-pre-wrap break-all">
                {errorDetails.traceback}
              </pre>
            </div>
          )}
          
          {/* 额外信息 */}
          {(errorDetails.url || errorDetails.method) && (
            <div className="grid grid-cols-2 gap-3 text-xs">
              {errorDetails.method && (
                <div className="bg-[#0a0a0a] border border-gray-800 rounded-lg p-2">
                  <span className="text-gray-500">Method:</span>
                  <span className="text-gray-300 ml-2 font-mono">{errorDetails.method}</span>
                </div>
              )}
              {errorDetails.url && (
                <div className="bg-[#0a0a0a] border border-gray-800 rounded-lg p-2">
                  <span className="text-gray-500">URL:</span>
                  <span className="text-gray-300 ml-2 font-mono truncate">{errorDetails.url}</span>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* 底部操作 */}
        <div className="flex items-center justify-between p-4 border-t border-gray-800 bg-[#0a0a0a]">
          <p className="text-gray-600 text-xs">
            复制错误信息可帮助开发者快速定位问题
          </p>
          <div className="flex gap-2">
            <button
              onClick={handleCopy}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                copied 
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700'
              }`}
            >
              {copied ? '✓ 已复制' : '📋 复制日志'}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg text-sm font-medium hover:bg-red-500/30 transition-colors border border-red-500/30"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * 错误提示条组件 - 可点击查看详情
 */
export const ErrorAlert = ({ message, errorDetails, className = '' }) => {
  const [showModal, setShowModal] = useState(false);
  const hasDetails = errorDetails && (errorDetails.traceback || errorDetails.error_type);

  return (
    <>
      <div 
        className={`bg-red-500/10 border border-red-500/30 rounded-xl p-4 ${hasDetails ? 'cursor-pointer hover:bg-red-500/15 transition-colors' : ''} ${className}`}
        onClick={() => hasDetails && setShowModal(true)}
      >
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center flex-shrink-0">
            <span className="text-red-400">⚠️</span>
          </div>
          <div className="flex-1">
            <p className="text-red-400 font-medium">{message || '发生错误'}</p>
            {hasDetails && (
              <p className="text-red-400/60 text-xs mt-1 flex items-center gap-1">
                <span>📋</span>
                点击查看详细错误日志
              </p>
            )}
          </div>
        </div>
      </div>
      
      {hasDetails && (
        <ErrorLogModal 
          isOpen={showModal} 
          onClose={() => setShowModal(false)} 
          errorDetails={errorDetails} 
        />
      )}
    </>
  );
};

export default ErrorLogModal;
