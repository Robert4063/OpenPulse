import React, { useState, useRef, useEffect } from 'react';

// MaxKB嵌入配置
const MAXKB_EMBED_URL = 'https://41cadc32.r1.cpolar.top/chat/api/embed?protocol=https&host=41cadc32.r1.cpolar.top&token=e6a447bdc1c14ec9';

// 创建iframe内嵌的HTML内容
const getIframeContent = () => `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
    }
    #maxkb, [id^="maxkb"] {
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      right: 0 !important;
      bottom: 0 !important;
      width: 100% !important;
      height: 100% !important;
      max-width: 100% !important;
      max-height: 100% !important;
      border-radius: 0 !important;
      box-shadow: none !important;
    }
    .maxkb-btn, [class*="maxkb-btn"] {
      display: none !important;
    }
  </style>
</head>
<body>
  <script async defer src="${MAXKB_EMBED_URL}"></script>
  <script>
    let attempts = 0;
    const maxAttempts = 50;
    const checkAndOpen = () => {
      attempts++;
      const btn = document.querySelector('[class*="maxkb"]') || document.querySelector('#maxkb');
      if (btn) {
        if (typeof window.maxkb !== 'undefined' && window.maxkb.open) {
          window.maxkb.open();
        } else {
          btn.click && btn.click();
        }
        // 通知父窗口加载完成
        window.parent.postMessage({ type: 'maxkb-loaded' }, '*');
      } else if (attempts < maxAttempts) {
        setTimeout(checkAndOpen, 200);
      }
    };
    setTimeout(checkAndOpen, 500);
  </script>
</body>
</html>
`;

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
  const [shouldRenderIframe, setShouldRenderIframe] = useState(false);
  const iconRef = useRef(null);
  const chatContainerRef = useRef(null);

  // 页面加载后延迟预加载iframe（后台预加载）
  useEffect(() => {
    const timer = setTimeout(() => {
      setShouldRenderIframe(true);
    }, 2000); // 页面加载2秒后开始预加载
    
    return () => clearTimeout(timer);
  }, []);

  // 监听iframe消息
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data && event.data.type === 'maxkb-loaded') {
        setIsLoaded(true);
      }
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

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
      if (!isOpen) {
        // 如果还没开始预加载，立即开始
        setShouldRenderIframe(true);
      }
      setIsOpen(!isOpen);
    }
  };

  // iframe加载完成
  const handleIframeLoad = () => {
    // 基础加载完成，但MaxKB可能还在初始化
    setTimeout(() => {
      if (!isLoaded) {
        setIsLoaded(true); // 备用：10秒后强制设为已加载
      }
    }, 10000);
  };

  // 计算聊天框位置
  const getChatPosition = () => {
    const iconCenterX = position.x + 28;
    const iconCenterY = position.y + 28;
    const chatWidth = 400;
    const chatHeight = 580;
    
    let chatX, chatY;
    
    if (iconCenterX < window.innerWidth / 2) {
      chatX = position.x + 66;
    } else {
      chatX = position.x - chatWidth - 10;
    }
    
    if (iconCenterY < window.innerHeight / 2) {
      chatY = position.y;
    } else {
      chatY = position.y - chatHeight + 56;
    }
    
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
        {/* 脉冲动画 */}
        {!isOpen && (
          <>
            <div className="ai-pulse-ring" />
            <div className="ai-pulse-ring ai-pulse-ring-delayed" />
          </>
        )}
        
        {/* 预加载状态指示器 */}
        {!isOpen && shouldRenderIframe && !isLoaded && (
          <div className="ai-preload-indicator" />
        )}
        
        {/* 已加载指示器（绿点） */}
        {!isOpen && isLoaded && (
          <div className="ai-ready-indicator" />
        )}
        
        {/* 图标主体 */}
        <div className={`ai-icon-inner ${isOpen ? 'scale-90' : ''}`}>
          {isOpen ? <CloseIcon /> : <AiIcon />}
        </div>
      </div>

      {/* 预加载的iframe（隐藏状态） */}
      {shouldRenderIframe && (
        <div
          ref={chatContainerRef}
          className="ai-chat-container"
          style={{
            left: chatPos.x,
            top: chatPos.y,
            width: 400,
            height: 580,
            display: isOpen ? 'flex' : 'none',
            visibility: isOpen ? 'visible' : 'hidden'
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

          {/* 主体 */}
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
                <p className="text-xs text-gray-400 mt-2">首次加载可能需要几秒钟</p>
              </div>
            )}
            
            {/* MaxKB iframe */}
            <iframe
              className="ai-chat-iframe"
              srcDoc={getIframeContent()}
              onLoad={handleIframeLoad}
              style={{ opacity: isLoaded ? 1 : 0 }}
              allow="microphone"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            />
          </div>
        </div>
      )}
    </>
  );
};

export default AiAssistant;
