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

const ConsultationsWrapper = () => {
  const [consultations, setConsultations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchConsultations = async () => {
      try {
        const response = await api.get('/chat/consultation')
        const { data } = response
        setConsultations(data.consultations || [])
      } catch (error) {
        console.error('Erro ao buscar consultas:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchConsultations()
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
        Consultas do Usuário
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Cidade</TableCell>
            <TableCell>Especialidade</TableCell>
            <TableCell>Data</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {consultations.map((c, index) => (
            <TableRow key={index}>
              <TableCell>{c.city}</TableCell>
              <TableCell>{c.period}</TableCell>
              <TableCell>{c.speciality}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}

export default ConsultationsWrapper
