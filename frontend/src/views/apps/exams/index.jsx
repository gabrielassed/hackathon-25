'use client'

import api from '@/api'
import {
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from '@mui/material'
import { useEffect, useState } from 'react'

const ExamsWrapper = () => {
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchExams = async () => {
      try {
        const response = await api.get('/chat/exams')
        const { data } = response
        setExams(data.exams || [])
      } catch (error) {
        console.error('Erro ao buscar exames:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchExams()
  }, [])

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}>
        <CircularProgress />
      </div>
    )
  }

  return (
    <TableContainer component={Paper}>
      <Typography variant='h6' sx={{ p: 2 }}>
        Exames do Usuário
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Paciente</TableCell>
            <TableCell>Protocolo</TableCell>
            <TableCell>Exame</TableCell>
            <TableCell>Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {exams.map(exam => (
            <TableRow key={exam.exam_id}>
              <TableCell>{exam.exam_id}</TableCell>
              <TableCell>{exam.name}</TableCell>
              <TableCell>{exam.protocol_number}</TableCell>
              <TableCell>{exam.exam_type}</TableCell>
              <TableCell>{exam.status}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}

export default ExamsWrapper
