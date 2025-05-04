export interface Disease {
  id: string;
  nando_id?: string;
  name: string;
  nameKana?: string;
  nameEn?: string;
  overview?: string;
  characteristics?: string;
  patientCount?: number;
  search_keywords?: string[];
  disease_type?: string;
  parent_disease_id?: string;
  is_designated_intractable?: boolean;
  is_chronic_childhood?: boolean;
  is_searchable?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Organization {
  id: string;
  disease_id: string;
  name: string;
  url?: string;
  description?: string;
  contact?: string;
  type?: 'patient' | 'family' | 'support';
  verificationStatus: 'pending' | 'verified' | 'rejected';
  relevance_score?: number;
  source_url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SearchSettings {
  enableApproximateMatch: boolean;
  enableTwoStageVerification: boolean;
  requireHumanVerification: boolean;
  maxTokens: number;
}

export interface SearchResult {
  organizations: Organization[];
  searchStats?: {
    totalFound: number;
    verified: number;
    pending: number;
    rejected: number;
  };
}

export interface DiseaseCustomKeyword {
  id: number;
  disease_id: string;
  keyword: string;
  keyword_type?: string;
  added_by?: string;
  created_at?: string;
}
