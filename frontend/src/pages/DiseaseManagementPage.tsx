import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  TablePagination,
  Checkbox,
  Button,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  IconButton,
  ButtonGroup
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import DownloadIcon from '@mui/icons-material/Download';
import UploadIcon from '@mui/icons-material/Upload';
import { diseaseApi } from '../services/api';
import { Disease } from '../types';

interface DiseaseSearchableUpdate {
  disease_id: string;
  is_searchable: boolean;
}

const DiseaseManagementPage: React.FC = () => {
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [modifiedDiseases, setModifiedDiseases] = useState<DiseaseSearchableUpdate[]>([]);
  
  useEffect(() => {
    fetchDiseases();
  }, []);

  const fetchDiseases = async () => {
    try {
      setLoading(true);
      const response = await diseaseApi.getAll();
      setDiseases(response.data);
      setError(null);
    } catch (err) {
      setError('疾患データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setPage(0);
  };

  const handleCheckboxChange = (disease: Disease) => {
    const updatedDisease = { ...disease, is_searchable: !disease.is_searchable };
    
    setDiseases(prev => 
      prev.map(d => d.id === disease.id ? updatedDisease : d)
    );
    
    setModifiedDiseases(prev => {
      const existingIndex = prev.findIndex(d => d.disease_id === disease.id);
      if (existingIndex !== -1) {
        const updated = [...prev];
        updated[existingIndex] = {
          disease_id: disease.id,
          is_searchable: updatedDisease.is_searchable
        };
        return updated;
      } else {
        return [...prev, {
          disease_id: disease.id,
          is_searchable: updatedDisease.is_searchable
        }];
      }
    });
  };

  const handleGroupSelect = (prefix: string, select: boolean) => {
    const updatedDiseases = diseases.map(disease => {
      if (disease.nando_id && disease.nando_id.startsWith(`NANDO:${prefix}`)) {
        return { ...disease, is_searchable: select };
      }
      return disease;
    });
    
    setDiseases(updatedDiseases);
    
    // 変更された疾患のリストを更新
    const updates: DiseaseSearchableUpdate[] = [];
    updatedDiseases.forEach(disease => {
      if (disease.nando_id && disease.nando_id.startsWith(`NANDO:${prefix}`)) {
        updates.push({
          disease_id: disease.id,
          is_searchable: select
        });
      }
    });
    
    setModifiedDiseases(prev => {
      const newModified = [...prev];
      updates.forEach(update => {
        const existingIndex = newModified.findIndex(d => d.disease_id === update.disease_id);
        if (existingIndex !== -1) {
          newModified[existingIndex] = update;
        } else {
          newModified.push(update);
        }
      });
      return newModified;
    });
  };

  const handleSaveChanges = async () => {
    if (modifiedDiseases.length === 0) return;

    try {
      setLoading(true);
      await diseaseApi.batchUpdateSearchable(modifiedDiseases);
      setModifiedDiseases([]);
      setError(null);
      alert('変更を保存しました');
    } catch (err) {
      setError('変更の保存に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await diseaseApi.exportSearchable();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `searchable_diseases_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('エクスポートに失敗しました');
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setLoading(true);
      const response = await diseaseApi.importSearchableSettings(file);
      alert(response.data.message);
      fetchDiseases(); // 再読み込み
    } catch (err) {
      setError('インポートに失敗しました');
    } finally {
      setLoading(false);
      // ファイル入力をリセット
      event.target.value = '';
    }
  };

  const handlePageChange = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const filteredDiseases = diseases.filter(disease =>
    disease.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    disease.nando_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    disease.nameEn?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const paginatedDiseases = filteredDiseases.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  if (loading && diseases.length === 0) {
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
        <Typography variant="h4" component="h1" gutterBottom>
          疾患の検索対象管理
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ mb: 2, p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <TextField
              label="疾患を検索"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={handleSearchChange}
              sx={{ width: 300 }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    {searchTerm && (
                      <IconButton
                        aria-label="clear search"
                        onClick={handleClearSearch}
                        edge="end"
                        size="small"
                      >
                        <ClearIcon />
                      </IconButton>
                    )}
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <ButtonGroup variant="outlined" size="small">
                <Button onClick={() => handleGroupSelect('1', false)}>NANDO:1*を外す</Button>
                <Button onClick={() => handleGroupSelect('2', false)}>NANDO:2*を外す</Button>
                <Button onClick={() => handleGroupSelect('1', true)}>NANDO:1*を選択</Button>
                <Button onClick={() => handleGroupSelect('2', true)}>NANDO:2*を選択</Button>
              </ButtonGroup>
              
              <ButtonGroup variant="contained" size="small">
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={handleExport}
                >
                  エクスポート
                </Button>
                <Button
                  startIcon={<UploadIcon />}
                  component="label"
                >
                  インポート
                  <input
                    type="file"
                    hidden
                    accept=".xlsx,.xls"
                    onChange={handleImport}
                  />
                </Button>
              </ButtonGroup>
              
              <Button
                variant="contained"
                color="primary"
                onClick={handleSaveChanges}
                disabled={modifiedDiseases.length === 0 || loading}
              >
                変更を保存 ({modifiedDiseases.length})
              </Button>
            </Box>
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">検索対象</TableCell>
                  <TableCell>疾患名</TableCell>
                  <TableCell>NANDO ID</TableCell>
                  <TableCell>タイプ</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedDiseases.map((disease) => (
                  <TableRow key={disease.id}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={disease.is_searchable || false}
                        onChange={() => handleCheckboxChange(disease)}
                        disabled={loading}
                      />
                    </TableCell>
                    <TableCell>{disease.name}</TableCell>
                    <TableCell>{disease.nando_id}</TableCell>
                    <TableCell>{disease.disease_type}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            rowsPerPageOptions={[10, 25, 50, 100]}
            component="div"
            count={filteredDiseases.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handlePageChange}
            onRowsPerPageChange={handleRowsPerPageChange}
            labelRowsPerPage="表示件数:"
          />
        </Paper>
      </Box>
    </Container>
  );
};

export default DiseaseManagementPage;
