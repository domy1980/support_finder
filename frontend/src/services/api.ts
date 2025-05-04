import axios from 'axios';
import { Disease } from '../types';

// インポートはTypeScriptの型として使用されるものだけに限定
type Organization = any;
type SearchSettings = any;
type SearchResult = any;

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const diseaseApi = {
  getAll: () => api.get<Disease[]>('/diseases'),
  getById: (id: string) => api.get<Disease>(`/diseases/${id}`),
  getHierarchy: (id: string) => api.get(`/diseases/${id}/hierarchy`),
  create: (disease: Partial<Disease>) => api.post<Disease>('/diseases', disease),
  update: (id: string, disease: Partial<Disease>) => api.put<Disease>(`/diseases/${id}`, disease),
  delete: (id: string) => api.delete(`/diseases/${id}`),
  search: (query: string) => api.get<Disease[]>(`/diseases/search/${query}`),
  getSearchable: () => api.get<Disease[]>('/diseases/searchable'),
  getHierarchyStats: () => api.get('/diseases/hierarchy/stats'),
  
  // 検索対象管理用
  batchUpdateSearchable: (updates: Array<{ disease_id: string; is_searchable: boolean }>) =>
    api.post('/diseases/batch-update-searchable', updates),
  updateSearchable: (diseaseId: string, is_searchable: boolean) =>
    api.patch(`/diseases/${diseaseId}/searchable`, { is_searchable }),
  exportSearchable: () =>
    api.get('/diseases/searchable/export', { responseType: 'blob' }),
  importSearchableSettings: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/diseases/searchable/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  // キーワード関連
  addKeyword: (diseaseId: string, keywordData: { keyword: string; keyword_type: string; added_by: string }) => 
    api.post(`/diseases/${diseaseId}/keywords`, keywordData),
  getKeywords: (diseaseId: string) => 
    api.get(`/diseases/${diseaseId}/keywords`),
  deleteKeyword: (keywordId: number) => 
    api.delete(`/diseases/keywords/${keywordId}`),
  importKeywords: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/diseases/keywords/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

export const searchApi = {
  searchForDisease: (diseaseId: string, settings: SearchSettings) => 
    api.post<SearchResult>(`/search/disease/${diseaseId}`, settings),
  getSearchTerms: (diseaseId: string) => 
    api.get(`/search/terms/${diseaseId}`),
};

export const verificationApi = {
  verifyOrganization: (orgId: string, status: string, reason?: string) =>
    api.post(`/verification/verify/${orgId}`, { status, reason }),
};

export const nandoApi = {
  importData: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/nando/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  importCustomDiseases: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/nando/import/custom', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getHierarchy: () => api.get('/nando/hierarchy'),
  runComprehensiveSearch: () => api.post('/nando/search/comprehensive'),
};

export default api;
