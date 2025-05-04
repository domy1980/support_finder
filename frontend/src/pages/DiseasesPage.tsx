////frontend/src/pages/DiseasePage.tsx

import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, List, ListItem, ListItemText, 
  CircularProgress, Alert, TextField, Paper, Pagination, Chip 
} from '@mui/material';
import { Link } from 'react-router-dom';
import { diseaseApi } from '../services/api';
import { Disease } from '../types';

const DiseasesPage: React.FC = () => {
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 50;

  useEffect(() => {
    const fetchDiseases = async () => {
      try {
        const response = await diseaseApi.getAll();
        setDiseases(response.data);
        setTotalPages(Math.ceil(response.data.length / itemsPerPage));
        setLoading(false);
      } catch (err) {
        setError('疾患データの取得に失敗しました');
        setLoading(false);
      }
    };

    fetchDiseases();
  }, []);

  const filteredDiseases = diseases.filter(disease => {
    const query = searchQuery.toLowerCase();
    return (
      disease.name.toLowerCase().includes(query) ||
      disease.nameKana?.toLowerCase().includes(query) ||
      disease.nameEn?.toLowerCase().includes(query) ||
      disease.nando_id?.toLowerCase().includes(query) ||
      disease.search_keywords?.some(keyword => 
        keyword.toLowerCase().includes(query)
      )
    );
  });

  const paginatedDiseases = filteredDiseases.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" mt={5}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Box mt={5}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          疾患一覧
        </Typography>
        
        <Typography variant="subtitle1" sx={{ mb: 2 }}>
          全 {diseases.length} 疾患
        </Typography>
        
        <TextField
          fullWidth
          label="疾患を検索（疾患名、英語名、NANDO ID、類義語で検索可能）"
          variant="outlined"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setPage(1);
          }}
          sx={{ mb: 3 }}
          placeholder="例：ALS、筋萎縮性側索硬化症、NANDO:1200002"
        />

        <Paper elevation={1}>
          <List>
            {paginatedDiseases.map((disease) => (
              <ListItem
                key={disease.id}
                component={Link}
                to={`/diseases/${disease.id}`}
                sx={{
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">
                        {disease.name}
                      </Typography>
                      {disease.nando_id && (
                        <Chip 
                          label={disease.nando_id} 
                          size="small" 
                          variant="outlined"
                          color="primary"
                        />
                      )}
                      {disease.parent_disease_id && (
                        <Chip 
                          label={`親: ${disease.parent_disease_id}`} 
                          size="small" 
                          variant="outlined"
                          color="secondary"
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <>
                      {disease.nameKana && <div>読み: {disease.nameKana}</div>}
                      {disease.nameEn && <div>英語: {disease.nameEn}</div>}
                      {disease.overview && <div>{disease.overview}</div>}
                      {disease.search_keywords && disease.search_keywords.length > 0 && (
                        <div>
                          検索キーワード: {disease.search_keywords.join(', ')}
                        </div>
                      )}
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>

        {filteredDiseases.length === 0 && (
          <Typography color="text.secondary" align="center" sx={{ mt: 3 }}>
            該当する疾患が見つかりません
          </Typography>
        )}

        {filteredDiseases.length > itemsPerPage && (
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
            <Pagination
              count={Math.ceil(filteredDiseases.length / itemsPerPage)}
              page={page}
              onChange={handlePageChange}
              color="primary"
            />
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default DiseasesPage;
