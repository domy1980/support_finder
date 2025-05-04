//frontend/src/pages/DiseaseDetailPage.tsx

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Container, Typography, Box, Paper, Button, CircularProgress, Alert,
  Divider, Chip, TextField, Dialog, DialogTitle, DialogContent, 
  DialogActions, Select, MenuItem, FormControl, InputLabel, Card, CardContent
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import { diseaseApi } from '../services/api';
import { Disease, DiseaseCustomKeyword } from '../types';

const DiseaseDetailPage: React.FC = () => {
  const { diseaseId } = useParams<{ diseaseId: string }>();
  const [disease, setDisease] = useState<Disease | null>(null);
  const [hierarchy, setHierarchy] = useState<any>(null);
  const [keywords, setKeywords] = useState<DiseaseCustomKeyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newKeyword, setNewKeyword] = useState('');
  const [keywordType, setKeywordType] = useState('symptom');

  useEffect(() => {
    const fetchDisease = async () => {
      if (!diseaseId) {
        setError('疾患IDが指定されていません');
        setLoading(false);
        return;
      }
      
      try {
        console.log('Fetching disease with ID:', diseaseId);
        
        // 疾患情報を取得
        const response = await diseaseApi.getById(diseaseId);
        console.log('Disease data received:', response.data);
        setDisease(response.data);
        
        // 階層情報を取得
        try {
          const hierarchyResponse = await diseaseApi.getHierarchy(diseaseId);
          console.log('Hierarchy data received:', hierarchyResponse.data);
          setHierarchy(hierarchyResponse.data);
        } catch (hierErr) {
          console.error('Failed to fetch hierarchy:', hierErr);
          // 階層情報の取得に失敗しても続行
        }
        
        // カスタムキーワードを取得
        try {
          const keywordsResponse = await diseaseApi.getKeywords(diseaseId);
          console.log('Keywords data received:', keywordsResponse.data);
          setKeywords(keywordsResponse.data.keywords || []);
        } catch (keyErr) {
          console.error('Failed to fetch keywords:', keyErr);
          // キーワードの取得に失敗しても続行
        }
        
      } catch (err) {
        console.error('Error fetching disease:', err);
        setError('疾患データの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchDisease();
  }, [diseaseId]);

  const handleAddKeyword = async () => {
    if (!newKeyword.trim() || !diseaseId) return;

    try {
      await diseaseApi.addKeyword(diseaseId, {
        keyword: newKeyword,
        keyword_type: keywordType,
        added_by: 'manual'
      });

      // キーワードを再取得
      const keywordsResponse = await diseaseApi.getKeywords(diseaseId);
      setKeywords(keywordsResponse.data.keywords || []);
      
      setOpenDialog(false);
      setNewKeyword('');
    } catch (err) {
      console.error('Failed to add keyword:', err);
    }
  };

  const handleDeleteKeyword = async (keywordId: number) => {
    try {
      await diseaseApi.deleteKeyword(keywordId);
      
      // キーワードを再取得
      if (diseaseId) {
        const keywordsResponse = await diseaseApi.getKeywords(diseaseId);
        setKeywords(keywordsResponse.data.keywords || []);
      }
    } catch (err) {
      console.error('Failed to delete keyword:', err);
    }
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

  if (error || !disease) {
    return (
      <Container>
        <Box mt={5}>
          <Alert severity="error">
            {error || '疾患が見つかりません'}
            <br />
            疾患ID: {diseaseId}
          </Alert>
          <Button
            component={Link}
            to="/diseases"
            startIcon={<ArrowBackIcon />}
            sx={{ mt: 2 }}
          >
            疾患一覧に戻る
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Button
          component={Link}
          to="/diseases"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 3 }}
        >
          疾患一覧に戻る
        </Button>

        <Paper elevation={3} sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h4" component="h1">
              {disease.name}
            </Typography>
            {disease.nando_id && (
              <Chip 
                label={`NANDO: ${disease.nando_id}`} 
                color="primary"
                variant="outlined"
              />
            )}
          </Box>

          {/* 階層情報 */}
          {hierarchy && (
            <Card variant="outlined" sx={{ mb: 3, bgcolor: 'grey.50' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  階層情報
                </Typography>
                
                {hierarchy.parent && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      親疾患
                    </Typography>
                    <Chip
                      label={`${hierarchy.parent.name} (${hierarchy.parent.nando_id})`}
                      component={Link}
                      to={`/diseases/${hierarchy.parent.id}`}
                      clickable
                      color="secondary"
                      variant="outlined"
                    />
                  </Box>
                )}
                
                {hierarchy.children && hierarchy.children.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      子疾患
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                      {hierarchy.children.map((child: any) => (
                        <Chip
                          key={child.id}
                          label={`${child.name} (${child.nando_id})`}
                          component={Link}
                          to={`/diseases/${child.id}`}
                          clickable
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}

          {disease.nameKana && (
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              {disease.nameKana}
            </Typography>
          )}

          {disease.nameEn && (
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              {disease.nameEn}
            </Typography>
          )}

          <Divider sx={{ my: 2 }} />

          {disease.overview && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                概要
              </Typography>
              <Typography variant="body1">
                {disease.overview}
              </Typography>
            </Box>
          )}

          {disease.characteristics && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                疾患の特徴
              </Typography>
              <Typography variant="body1">
                {disease.characteristics}
              </Typography>
            </Box>
          )}

          {disease.patientCount !== undefined && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                患者数
              </Typography>
              <Typography variant="body1">
                約 {disease.patientCount.toLocaleString()} 人
              </Typography>
            </Box>
          )}

          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6">
                検索キーワード
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setOpenDialog(true)}
                size="small"
              >
                キーワード追加
              </Button>
            </Box>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {disease.search_keywords && disease.search_keywords.map((keyword: string, index: number) => (
                <Chip key={index} label={keyword} variant="outlined" />
              ))}
            </Box>
          </Box>

          {keywords.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                カスタムキーワード
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {keywords.map((keyword) => (
                  <Chip
                    key={keyword.id}
                    label={`${keyword.keyword} (${keyword.keyword_type})`}
                    onDelete={() => handleDeleteKeyword(keyword.id)}
                    color={keyword.keyword_type === 'symptom' ? 'primary' : 'secondary'}
                  />
                ))}
              </Box>
            </Box>
          )}

          <Divider sx={{ my: 3 }} />

          <Button
            variant="contained"
            color="primary"
            component={Link}
            to={`/search/${disease.id}`}
            size="large"
            startIcon={<SearchIcon />}
          >
            この疾患の支援団体を検索
          </Button>
        </Paper>
      </Box>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>キーワード追加</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="キーワード"
            fullWidth
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>キーワードタイプ</InputLabel>
            <Select
              value={keywordType}
              onChange={(e) => setKeywordType(e.target.value)}
              label="キーワードタイプ"
            >
              <MenuItem value="symptom">症状</MenuItem>
              <MenuItem value="treatment">治療</MenuItem>
              <MenuItem value="other">その他</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>キャンセル</Button>
          <Button onClick={handleAddKeyword} variant="contained">追加</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default DiseaseDetailPage;
