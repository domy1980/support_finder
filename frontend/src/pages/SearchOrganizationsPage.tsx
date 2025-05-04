////frontend/src/pages/SearchOrganizationsPage.tsx

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Container, Typography, Box, Paper, Button, CircularProgress,
  Alert, List, ListItem, ListItemText, Chip, Card, CardContent,
  CardActions, Divider, LinearProgress
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SearchIcon from '@mui/icons-material/Search';
import { diseaseApi, searchApi } from '../services/api';
import { Disease, Organization } from '../types';

const SearchOrganizationsPage: React.FC = () => {
  const { diseaseId } = useParams<{ diseaseId: string }>();
  const [disease, setDisease] = useState<Disease | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerms, setSearchTerms] = useState<string[]>([]);

  useEffect(() => {
    const fetchDisease = async () => {
      if (!diseaseId) return;
      
      try {
        setLoading(true);
        const response = await diseaseApi.getById(diseaseId);
        setDisease(response.data);
        
        // 検索語を取得
        const termsResponse = await searchApi.getSearchTerms(diseaseId);
        setSearchTerms(termsResponse.data.search_terms || []);
      } catch (err) {
        setError('疾患データの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchDisease();
  }, [diseaseId]);

  const handleSearch = async () => {
    if (!diseaseId) return;

    try {
      setSearching(true);
      setError(null);
      const response = await searchApi.searchForDisease(diseaseId, {
        enableApproximateMatch: true,
        enableTwoStageVerification: true,
        requireHumanVerification: false,
        maxTokens: 4000
      });
      
      setOrganizations(response.data.organizations || []);
    } catch (err) {
      setError('検索中にエラーが発生しました');
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  if (loading || !disease) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" mt={5}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Button
          component={Link}
          to={`/diseases/${diseaseId}`}
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 3 }}
        >
          疾患詳細に戻る
        </Button>

        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            支援団体検索
          </Typography>
          
          <Typography variant="h6" gutterBottom>
            {disease.name}
          </Typography>
          
          {disease.nameEn && (
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              {disease.nameEn}
            </Typography>
          )}

          <Divider sx={{ my: 2 }} />

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              検索キーワード:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {searchTerms.map((term, index) => (
                <Chip key={index} label={term} variant="outlined" />
              ))}
            </Box>
          </Box>

          <Button
            variant="contained"
            size="large"
            startIcon={<SearchIcon />}
            onClick={handleSearch}
            disabled={searching}
          >
            {searching ? '検索中...' : '支援団体を検索'}
          </Button>

          {searching && (
            <Box sx={{ width: '100%', mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Web検索を実行しています...
              </Typography>
            </Box>
          )}
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {organizations.length > 0 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              検索結果: {organizations.length}件
            </Typography>
            
            <List>
              {organizations.map((org) => (
                <Card key={org.id} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {org.name}
                    </Typography>
                    
                    {org.type && (
                      <Chip
                        label={
                          org.type === 'patient' ? '患者会' :
                          org.type === 'family' ? '家族会' :
                          '支援団体'
                        }
                        color="primary"
                        size="small"
                        sx={{ mb: 1 }}
                      />
                    )}
                    
                    {org.description && (
                      <Typography variant="body1" paragraph>
                        {org.description}
                      </Typography>
                    )}
                    
                    {org.url && (
                      <Typography variant="body2" color="primary">
                        <a href={org.url} target="_blank" rel="noopener noreferrer">
                          {org.url}
                        </a>
                      </Typography>
                    )}
                    
                    {org.contact && (
                      <Typography variant="body2" color="text.secondary">
                        連絡先: {org.contact}
                      </Typography>
                    )}
                    
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        label={`検証状態: ${org.verificationStatus}`}
                        variant="outlined"
                        size="small"
                        color={
                          org.verificationStatus === 'verified' ? 'success' :
                          org.verificationStatus === 'rejected' ? 'error' :
                          'default'
                        }
                      />
                      
                      {org.relevance_score && (
                        <Chip
                          label={`関連性スコア: ${org.relevance_score}`}
                          variant="outlined"
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </List>
          </Paper>
        )}

        {!searching && organizations.length === 0 && !error && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography color="text.secondary" align="center">
              検索ボタンをクリックして、支援団体を検索してください。
            </Typography>
          </Paper>
        )}
      </Box>
    </Container>
  );
};

export default SearchOrganizationsPage;
