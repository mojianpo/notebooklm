import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 360000 // 增加到 300 秒，确保脑图生成有足够时间
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
