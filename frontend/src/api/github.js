import axios from 'axios';

const API_BASE = '/api/v1';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE,
  timeout: 8000,  // 8秒超时，更快显示错误
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 自定义错误类，包含详细的后端错误信息
 */
export class ApiError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = 'ApiError';
    this.details = details;
  }
}

// 响应拦截器 - 捕获并转换错误信息
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 构建详细的错误信息
    let errorDetails = {
      timestamp: new Date().toISOString(),
      request_path: error.config ? `${error.config.method?.toUpperCase()} ${error.config.url}` : '未知',
    };

    if (error.response) {
      // 服务器返回了错误响应
      const data = error.response.data;
      
      if (data && data.error) {
        // 后端返回的详细错误信息
        errorDetails = {
          ...errorDetails,
          error_type: data.error_type || 'ServerError',
          message: data.message || '服务器错误',
          traceback: data.traceback || null,
          log_details: data.log_details || null,
          timestamp: data.timestamp || errorDetails.timestamp,
          request_path: data.request_path || errorDetails.request_path,
        };
      } else {
        // 普通 HTTP 错误
        errorDetails = {
          ...errorDetails,
          error_type: `HTTP ${error.response.status}`,
          message: getHttpErrorMessage(error.response.status),
          traceback: null,
        };
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorDetails = {
        ...errorDetails,
        error_type: 'NetworkError',
        message: '无法连接到服务器，请检查网络连接或后端服务是否正常运行',
        traceback: `请求配置:\n  URL: ${error.config?.url || '未知'}\n  方法: ${error.config?.method?.toUpperCase() || '未知'}\n  超时: ${error.config?.timeout || '未知'}ms\n\n可能的原因:\n  1. 后端服务未启动\n  2. 网络连接问题\n  3. 请求超时`,
      };
    } else {
      // 请求配置错误
      errorDetails = {
        ...errorDetails,
        error_type: 'RequestError',
        message: error.message || '请求配置错误',
        traceback: null,
      };
    }

    // 创建自定义错误对象
    const apiError = new ApiError(errorDetails.message, errorDetails);
    return Promise.reject(apiError);
  }
);

// HTTP 状态码错误信息映射
function getHttpErrorMessage(status) {
  const messages = {
    400: '请求参数错误',
    401: '未授权，请登录',
    403: '拒绝访问',
    404: '请求的资源不存在',
    408: '请求超时',
    500: '服务器内部错误',
    502: '网关错误',
    503: '服务暂不可用',
    504: '网关超时',
  };
  return messages[status] || `服务器错误 (${status})`;
}

/**
 * 搜索项目
 * @param {Object} params - 搜索参数
 * @param {string} params.keyword - 关键词
 * @param {number} params.stars_min - 最小stars
 * @param {number} params.stars_max - 最大stars
 * @param {number} params.limit - 返回数量
 * @param {number} params.offset - 偏移量
 */
export const searchProjects = async (params) => {
  const response = await api.get('/search/projects', { params });
  return response.data;
};

/**
 * 获取项目列表
 * @param {number} limit - 返回数量
 */
export const getProjectList = async (limit = 100) => {
  const response = await api.get('/search/projects/list', { params: { limit } });
  return response.data;
};

/**
 * 获取排名靠前的项目
 * @param {number} limit - 返回数量（默认3）
 */
export const getTopProjects = async (limit = 3) => {
  const response = await api.get('/search/projects/top', { params: { limit } });
  return response.data;
};

/**
 * 获取项目所有趋势数据
 * @param {string} project - 项目名称 (owner/repo 或 owner_repo)
 * @param {string} start_date - 开始日期
 * @param {string} end_date - 结束日期
 */
export const getProjectTrends = async (project, start_date = null, end_date = null) => {
  const params = { project };
  if (start_date) params.start_date = start_date;
  if (end_date) params.end_date = end_date;
  
  const response = await api.get('/stats/project/trends', { params });
  return response.data;
};

/**
 * 获取Stars趋势
 */
export const getStarsTrend = async (project, start_date = null, end_date = null) => {
  const params = { project };
  if (start_date) params.start_date = start_date;
  if (end_date) params.end_date = end_date;
  
  const response = await api.get('/stats/stars/trend', { params });
  return response.data;
};

/**
 * 获取Forks趋势
 */
export const getForksTrend = async (project, start_date = null, end_date = null) => {
  const params = { project };
  if (start_date) params.start_date = start_date;
  if (end_date) params.end_date = end_date;
  
  const response = await api.get('/stats/forks/trend', { params });
  return response.data;
};

/**
 * 获取Watches趋势
 */
export const getWatchesTrend = async (project, start_date = null, end_date = null) => {
  const params = { project };
  if (start_date) params.start_date = start_date;
  if (end_date) params.end_date = end_date;
  
  const response = await api.get('/stats/watches/trend', { params });
  return response.data;
};

/**
 * 获取项目摘要
 */
export const getProjectSummary = async (project) => {
  const response = await api.get('/stats/project/summary', { params: { project } });
  return response.data;
};

/**
 * 获取项目贡献者统计
 * @param {string} project - 项目名称
 * @param {number} top_n - 返回 Top N 贡献者
 */
export const getContributors = async (project, top_n = 10) => {
  const response = await api.get('/stats/contributors', { params: { project, top_n } });
  return response.data;
};

/**
 * 获取贡献者饼图数据
 * @param {string} project - 项目名称
 * @param {number} top_n - 返回 Top N 贡献者
 */
export const getContributorsChart = async (project, top_n = 10) => {
  const response = await api.get('/stats/contributors/chart', { params: { project, top_n } });
  return response.data;
};

/**
 * 获取项目健康度评分（完整版）
 * @param {string} project - 项目名称 (owner/repo 或 owner_repo)
 */
export const getHealthScore = async (project) => {
  const response = await api.get('/health/score', { params: { project } });
  return response.data;
};

/**
 * 获取项目健康度评分摘要
 * @param {string} project - 项目名称 (owner/repo 或 owner_repo)
 */
export const getHealthSummary = async (project) => {
  const response = await api.get('/health/summary', { params: { project } });
  return response.data;
};

/**
 * 获取与指定项目健康度相似的项目
 * @param {string} project - 项目名称 (owner/repo 或 owner_repo)
 * @param {number} limit - 返回相似项目数量（默认5）
 */
export const getSimilarProjects = async (project, limit = 5) => {
  const response = await api.get('/health/similar', { params: { project, limit } });
  return response.data;
};

/**
 * 获取项目使用的编程语言信息
 * @param {string} project - 项目名称 (owner/repo 或 owner_repo)
 */
export const getProjectLanguages = async (project) => {
  const response = await api.get('/health/languages', { params: { project } });
  return response.data;
};

export default api;
