import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import HomePage from './pages/HomePage';
import LLMTestPage from './pages/LLMTestPage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Disease Support Finder
            </Typography>
            <Button color="inherit" component={Link} to="/">
              ホーム
            </Button>
            <Button color="inherit" component={Link} to="/llm-test">
              LLMテスト
            </Button>
          </Toolbar>
        </AppBar>
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/llm-test" element={<LLMTestPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
