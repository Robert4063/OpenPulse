import React, { useState, useRef, useEffect } from 'react';

// AI图标
const AiIcon = () => (
  <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
  </svg>
);

// 关闭图标
const CloseIcon = () => (
  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const AiAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ x: 30, y: window.innerHeight - 90 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [isLoaded, setIsLoaded] = useState(false);
  const iconRef = useRef(null);
  const chatContainerRef = useRef(null);

  // 处理拖拽开始
  const handleMouseDown = (e) => {
    if (isOpen) return;
    setIsDragging(true);
    const rect = iconRef.current.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };

  // 处理拖拽移动
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      
      const newX = e.clientX - dragOffset.x;
      const newY = e.clientY - dragOffset.y;
      
      // 限制在窗口范围内
      const maxX = window.innerWidth - 56;
      const maxY = window.innerHeight - 56;
      
      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  // 点击图标
  const handleClick = () => {
    if (!isDragging) {
      setIsOpen(!isOpen);
    }
  };

  // iframe加载完成
  const handleIframeLoad = () => {
    setIsLoaded(true);
  };

  // 计算聊天框位置
  const getChatPosition = () => {
    const iconCenterX = position.x + 28;
    const iconCenterY = position.y + 28;
    const chatWidth = 380;
    const chatHeight = 520;
    
    let chatX, chatY;
    
    // 根据图标位置决定聊天框方向
    if (iconCenterX < window.innerWidth / 2) {
      // 图标在左边，聊天框在右边
      chatX = position.x + 66;
    } else {
      // 图标在右边，聊天框在左边
      chatX = position.x - chatWidth - 10;
    }
    
    if (iconCenterY < window.innerHeight / 2) {
      // 图标在上面，聊天框在下面
      chatY = position.y;
    } else {
      // 图标在下面，聊天框在上面
      chatY = position.y - chatHeight + 56;
    }
    
    // 边界检查
    chatX = Math.max(10, Math.min(chatX, window.innerWidth - chatWidth - 10));
    chatY = Math.max(10, Math.min(chatY, window.innerHeight - chatHeight - 10));
    
    return { x: chatX, y: chatY };
  };

  const chatPos = getChatPosition();

  return (
    <>
      {/* 可拖拽的AI图标 */}
      <div
        ref={iconRef}
        className="ai-assistant-icon"
        style={{
          left: position.x,
          top: position.y,
          cursor: isDragging ? 'grabbing' : 'grab'
        }}
        onMouseDown={handleMouseDown}
        onClick={handleClick}
      >
        {/* 脉冲动画 - 圆形 */}
        {!isOpen && (
          <>
            <div className="ai-pulse-ring" />
            <div className="ai-pulse-ring ai-pulse-ring-delayed" />
          </>
        )}
        
        {/* 图标主体 - 圆形 */}
        <div className={`ai-icon-inner ${isOpen ? 'scale-90' : ''}`}>
          {isOpen ? <CloseIcon /> : <AiIcon />}
        </div>
      </div>

      {/* 聊天框 */}
      {isOpen && (
        <div
          ref={chatContainerRef}
          className="ai-chat-container"
          style={{
            left: chatPos.x,
            top: chatPos.y
          }}
        >
          {/* 头部 */}
          <div className="ai-chat-header">
            <div className="flex items-center gap-3">
              <div className="ai-chat-avatar">
                <AiIcon />
              </div>
              <div>
                <h3 className="text-white font-medium text-sm">AI 助手</h3>
                <p className="text-gray-400 text-xs">OpenPulse 项目顾问</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="ai-chat-close"
            >
              <CloseIcon />
            </button>
          </div>

          {/* 主体 - iframe */}
          <div className="ai-chat-body">
            {/* 加载提示 */}
            {!isLoaded && (
              <div className="ai-chat-loading">
                <div className="ai-loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p>正在连接 AI 服务...</p>
              </div>
            )}
            
            {/* Coze嵌入 */}
            <iframe
              className="ai-chat-iframe"
              src="https://www.coze.cn/store/bot/7513893821823926281?bot_id=true&hide_bot_info=1"
              onLoad={handleIframeLoad}
              style={{ opacity: isLoaded ? 1 : 0 }}
              allow="microphone"
            />
          </div>
        </div>
      )}
    </>
  );
};

export default AiAssistant;
