export interface Disease {
  id: string;
  name: string;
  nameKana: string;
  nameEn: string;
  overview: string;
  patientCount?: number;
}

export interface Organization {
  id: string;
  name: string;
  url?: string;
  description?: string;
  contact?: string;
  type: 'patient' | 'family' | 'support';
  verificationStatus: 'pending' | 'verified' | 'rejected';
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
