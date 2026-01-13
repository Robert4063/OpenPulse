import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 代理超时设置 - 后端无响应时快速返回错误
        timeout: 5000,
        proxyTimeout: 5000,
        configure: (proxy) => {
          proxy.on('error', (err, req, res) => {
            // 代理错误时返回友好的错误信息
            console.error('[Proxy Error]', err.message);
            if (res.writeHead && !res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({
                error: true,
                message: '无法连接到后端服务，请检查后端是否已启动',
                error_type: 'ProxyError',
                timestamp: new Date().toISOString(),
                request_path: `${req.method} ${req.url}`,
                traceback: `代理错误详情:\n  目标: http://127.0.0.1:8000\n  错误: ${err.message}\n  代码: ${err.code || 'UNKNOWN'}\n\n可能的原因:\n  1. 后端服务 (python main.py) 未启动\n  2. 后端服务端口 8000 被占用\n  3. 防火墙阻止了连接`
              }));
            }
          });
        }
      }
    }
  }
})
