export interface Disease {
  id: string;
  name: string;
  nameKana?: string;
  nameEn?: string;
  overview?: string;
  characteristics?: string;  // 追加
  patientCount?: number;
  search_keywords?: string[];  // 追加
  nando_id?: string;  // 追加
  disease_type?: string;  // 追加
  parent_disease_id?: string;  // 追加
  is_designated_intractable?: boolean;  // 追加
  is_chronic_childhood?: boolean;  // 追加
  created_at?: string;
  updated_at?: string;
}

export interface DiseaseSynonym {
  id: number;
  disease_id: string;
  synonym: string;
  language: string;
  created_at: string;
}

export interface DiseaseCustomKeyword {
  id: number;
  disease_id: string;
  keyword: string;
  keyword_type: string;
  added_by: string;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  url?: string;
  description?: string;
  contact?: string;
  type: 'patient' | 'family' | 'support';
  verificationStatus: 'pending' | 'verified' | 'rejected';
  disease_id?: string;
  relevance_score?: number;
  source_url?: string;
}

export interface SearchSettings {
  enableApproximateMatch: boolean;
  enableTwoStageVerification: boolean;
  requireHumanVerification: boolean;
  maxTokens: number;
}

export interface SearchResult {
  disease: Disease;
  organizations: Organization[];
  searchTimestamp: string;
}
