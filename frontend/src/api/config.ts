import api from './index'

export interface Config {
  id?: number
  key: string
  value: string
  description?: string
  category?: string
  created_at?: string
  updated_at?: string
  is_default?: boolean
}

export const configApi = {
  // 获取所有配置
  list: (category?: string) => 
    api.get<Config[]>('/config/', { params: { category } }),
  
  // 获取默认配置
  getDefaults: () => 
    api.get('/config/defaults'),
  
  // 获取单个配置
  get: (key: string) => 
    api.get<Config>(`/config/${key}`),
  
  // 创建或更新配置
  set: (key: string, value: string, description?: string, category?: string) => 
    api.post<Config>('/config/', null, { 
      params: { key, value, description, category } 
    }),
  
  // 更新配置
  update: (key: string, value: string) => 
    api.put<Config>(`/config/${key}`, null, { params: { value } }),
  
  // 删除配置（重置为默认值）
  delete: (key: string) => 
    api.delete(`/config/${key}`),
  
  // 重置为默认值
  reset: (keys?: string[]) => 
    api.post('/config/reset', null, { params: { keys } })
}
