import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          難病・希少疾患支援団体検索システム
        </Typography>
        <Typography variant="h6" color="text.secondary" paragraph>
          難病や希少疾患の患者会・支援団体を検索できるシステムです。
        </Typography>
        <Box sx={{ mt: 4 }}>
          <Button
            variant="contained"
            size="large"
            component={Link}
            to="/diseases"
          >
            疾患リストを見る
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default HomePage;
