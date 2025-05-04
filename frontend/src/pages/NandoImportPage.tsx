import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Button, Alert, CircularProgress,
  Paper, Input, Card, CardContent
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { nandoApi, diseaseApi } from '../services/api';

const NandoImportPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await diseaseApi.getHierarchyStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: 'error', text: 'ファイルを選択してください' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await nandoApi.importData(file);
      
      if (response.data.status === 'success') {
        setMessage({ 
          type: 'success', 
          text: `NANDOデータのインポートに成功しました。${response.data.imported}件のデータをインポートしました。` 
        });
        fetchStats(); // 統計情報を更新
      } else {
        setMessage({ 
          type: 'error', 
          text: `インポートに失敗しました: ${response.data.message}` 
        });
      }
      
      setFile(null);
      const fileInput = document.getElementById('nando-file-input') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'インポートに失敗しました' });
    } finally {
      setLoading(false);
    }
  };

  const handleComprehensiveSearch = async () => {
    setLoading(true);
    setMessage(null);

    try {
      await nandoApi.runComprehensiveSearch();
      setMessage({ type: 'success', text: '包括的な検索を開始しました。これには時間がかかる場合があります。' });
    } catch (error) {
      setMessage({ type: 'error', text: '検索の開始に失敗しました' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          NANDOデータ管理
        </Typography>

        {stats && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                疾患階層の統計情報
              </Typography>
              <Typography>
                総疾患数: {stats.total_diseases}
              </Typography>
              <Typography>
                検索対象疾患数: {stats.searchable_diseases}
              </Typography>
              <Typography>
                削減率: {stats.reduction_rate}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                除外カテゴリー: {stats.excluded_categories.join(', ')}
              </Typography>
            </CardContent>
          </Card>
        )}

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            NANDOデータのインポート
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            難病および小児慢性疾患のデータファイル（.xlsx）をアップロードしてください。
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Input
              type="file"
              onChange={handleFileChange}
              inputProps={{ accept: '.xlsx,.xls' }}
              sx={{ display: 'none' }}
              id="nando-file-input"
            />
            <label htmlFor="nando-file-input">
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUploadIcon />}
              >
                ファイルを選択
              </Button>
            </label>
            {file && <Typography>{file.name}</Typography>}
          </Box>

          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading ? <CircularProgress size={24} /> : 'インポート'}
          </Button>
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            包括的な検索
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            階層構造を考慮して、効率的に支援団体の検索を実行します。
          </Typography>
          
          <Button
            variant="contained"
            color="secondary"
            onClick={handleComprehensiveSearch}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : '包括的検索を実行'}
          </Button>
        </Paper>

        {message && (
          <Alert severity={message.type} sx={{ mt: 3 }}>
            {message.text}
          </Alert>
        )}
      </Box>
    </Container>
  );
};

export default NandoImportPage;
