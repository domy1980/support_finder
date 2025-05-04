import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import HomePage from './pages/HomePage';
import DiseasesPage from './pages/DiseasesPage';
import DiseaseDetailPage from './pages/DiseaseDetailPage';
import SearchOrganizationsPage from './pages/SearchOrganizationsPage';
import NandoImportPage from './pages/NandoImportPage';
import LLMTestPage from './pages/LLMTestPage';
import DiseaseManagementPage from './pages/DiseaseManagementPage';

function App() {
  return (
    <Router>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            難病・希少疾患支援団体検索システム
          </Typography>
          <Button color="inherit" component={Link} to="/">
            ホーム
          </Button>
          <Button color="inherit" component={Link} to="/diseases">
            疾患一覧
          </Button>
          <Button color="inherit" component={Link} to="/diseases/manage">
            検索対象管理
          </Button>
          <Button color="inherit" component={Link} to="/nando/import">
            NANDOインポート
          </Button>
          <Button color="inherit" component={Link} to="/llm/test">
            LLMテスト
          </Button>
        </Toolbar>
      </AppBar>
      <Container>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/diseases" element={<DiseasesPage />} />
          <Route path="/diseases/manage" element={<DiseaseManagementPage />} />
          <Route path="/diseases/:diseaseId" element={<DiseaseDetailPage />} />
          <Route path="/search/:diseaseId" element={<SearchOrganizationsPage />} />
          <Route path="/nando/import" element={<NandoImportPage />} />
          <Route path="/llm/test" element={<LLMTestPage />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
