'use client'

import api from '@/api'
import { Alert, Box, Button, CircularProgress, Container, Snackbar, Stack, TextField, Typography } from '@mui/material'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

const ChatContextScreen = () => {
  const [initialContext, setInitialContext] = useState('')
  const [contextText, setContextText] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [snack, setSnack] = useState({ open: false, severity: 'success', message: '' })
  const abortRef = useRef(false)

  const isDirty = useMemo(() => contextText !== initialContext, [contextText, initialContext])

  const showSnack = (message, severity = 'success') => setSnack({ open: true, severity, message })

  const closeSnack = () => setSnack(s => ({ ...s, open: false }))

  const loadContext = useCallback(async () => {
    setLoading(true)
    abortRef.current = false
    try {
      const { data } = await api.get('/chat/context')
      if (abortRef.current) return
      const ctx = typeof data === 'string' ? data : (data?.context ?? '')
      setInitialContext(ctx)
      setContextText(ctx)
    } catch (err) {
      console.error(err)
      showSnack('Não foi possível carregar o contexto.', 'error')
    } finally {
      if (!abortRef.current) setLoading(false)
    }
  }, [])

  const saveContext = useCallback(async () => {
    setSaving(true)
    try {
      await api.post('/chat/context', { context: contextText })
      setInitialContext(contextText)
      showSnack('Contexto salvo com sucesso!', 'success')
    } catch (err) {
      console.error(err)
      showSnack('Erro ao salvar o contexto.', 'error')
    } finally {
      setSaving(false)
    }
  }, [contextText])

  // Ctrl/Cmd + S para salvar
  useEffect(() => {
    const onKeyDown = e => {
      const isSave = (e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')
      if (isSave) {
        e.preventDefault()
        if (isDirty && !saving) saveContext()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [isDirty, saving, saveContext])

  useEffect(() => {
    loadContext()
    return () => {
      abortRef.current = true
    }
  }, [loadContext])

  return (
    <Container maxWidth='lg' sx={{ py: 4 }}>
      <Stack spacing={3}>
        <Box>
          <Typography variant='h5' fontWeight={600}>
            Contexto do Chat
          </Typography>
          <Typography variant='body2' color='text.secondary'>
            Edite abaixo o prompt-base/contexto utilizado pelo chatbot.
          </Typography>
        </Box>

        <Box
          sx={{
            position: 'relative',
            borderRadius: 2,
            overflow: 'hidden',
            bgcolor: 'background.paper',
            boxShadow: t => t.shadows[1],
            p: 2
          }}
        >
          {loading ? (
            <Box
              sx={{
                minHeight: 300,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <CircularProgress />
            </Box>
          ) : (
            <TextField
              value={contextText}
              onChange={e => setContextText(e.target.value)}
              placeholder='Cole ou escreva aqui o contexto do chat...'
              fullWidth
              multiline
              minRows={18}
              maxRows={Infinity}
              variant='outlined'
              InputProps={{ sx: { fontFamily: 'monospace', lineHeight: 1.5 } }}
            />
          )}
        </Box>

        <Stack direction='row' spacing={2} justifyContent='flex-end'>
          <Button variant='outlined' onClick={loadContext} disabled={loading || saving}>
            Recarregar
          </Button>
          <Button variant='contained' onClick={saveContext} disabled={!isDirty || saving || loading}>
            {saving ? 'Salvando...' : 'Salvar'}
          </Button>
        </Stack>
      </Stack>

      <Snackbar
        open={snack.open}
        autoHideDuration={3000}
        onClose={closeSnack}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={closeSnack} severity={snack.severity} variant='filled' sx={{ width: '100%' }}>
          {snack.message}
        </Alert>
      </Snackbar>
    </Container>
  )
}

export default ChatContextScreen
