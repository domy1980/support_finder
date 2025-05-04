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
};

export const searchApi = {
  searchForDisease: (diseaseId: string, settings: SearchSettings) => 
    api.post<SearchResult>(`/search/disease/${diseaseId}`, settings),
};

export const verificationApi = {
  verifyOrganization: (orgId: string, status: string, reason?: string) =>
    api.post(`/verification/verify/${orgId}`, { status, reason }),
};

export default api;
