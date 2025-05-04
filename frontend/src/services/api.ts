import axios from 'axios';
import { Disease, Organization, SearchSettings, SearchResult } from '../types';

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
  getHierarchy: () => api.get('/nando/hierarchy'),
  runComprehensiveSearch: () => api.post('/nando/search/comprehensive'),
};

export default api;
