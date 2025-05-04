////frontend/src/pages/LLMTestPage.tsx

import React, { useState } from 'react';
import { Container, Typography, Box, Button, TextField, Alert, CircularProgress } from '@mui/material';
import axios from 'axios';

const LLMTestPage: React.FC = () => {
  const [text, setText] = useState('');
  const [diseaseName, setDiseaseName] = useState('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<boolean | null>(null);

  const checkHealth = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/llm/health');
      setHealth(response.data.status === 'healthy');
    } catch (err) {
      setHealth(false);
    }
  };

  const testExtraction = async () => {
    if (!text || !diseaseName) {
      setError('テキストと疾患名を入力してください');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/llm/test-extraction', {
        text,
        disease_name: diseaseName
      });
      setResult(response.data);
    } catch (err) {
      setError('エラーが発生しました: ' + (err as any).message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    checkHealth();
  }, []);

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          LLM連携テスト
        </Typography>
        
        {health !== null && (
          <Alert severity={health ? "success" : "error"} sx={{ mb: 2 }}>
            LLMサービス: {health ? "正常" : "接続できません"}
          </Alert>
        )}

        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="疾患名"
            value={diseaseName}
            onChange={(e) => setDiseaseName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            multiline
            rows={4}
            label="テキスト"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="例: 日本ALS協会は、筋萎縮性側索硬化症（ALS）の患者とその家族を支援する団体です。"
          />
        </Box>

        <Button
          variant="contained"
          onClick={testExtraction}
          disabled={loading || !health}
        >
          {loading ? <CircularProgress size={24} /> : '情報抽出テスト'}
        </Button>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              抽出結果:
            </Typography>
            <pre style={{ 
              backgroundColor: '#f5f5f5', 
              padding: '16px', 
              borderRadius: '4px',
              overflow: 'auto'
            }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default LLMTestPage;
