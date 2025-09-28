// Third-party Imports
import { createSlice, nanoid } from '@reduxjs/toolkit'

// Data Imports
import api from '@/api'
import { db } from '@/fake-db/apps/chat'

const moveActiveChatToTop = state => {
  state.chats = state.chats.filter(c => c.userId !== state.activeUser?.id)
  const existing = state.chats.find(c => c.userId === state.activeUser?.id)
  // se removeu, existing vira undefined; então buscamos de novo antes de unshift
  const chat = state.chats.find(c => c.userId === state.activeUser?.id) || existing
  if (chat) state.chats.unshift(chat)
}

// --- Reducers síncronos para manipular mensagens ---
const chatSlice = createSlice({
  name: 'chat',
  initialState: db,
  reducers: {
    getActiveUserData: (state, action) => {
      const activeUser = state.contacts.find(user => user.id === action.payload)
      const chat = state.chats.find(chat => chat.userId === action.payload)

      if (chat && chat.unseenMsgs > 0) chat.unseenMsgs = 0
      if (activeUser) state.activeUser = activeUser
    },
    addNewChat: (state, action) => {
      const { id } = action.payload
      state.contacts.find(contact => {
        if (contact.id === id && !state.chats.find(chat => chat.userId === contact.id)) {
          state.chats.unshift({
            id: state.chats.length + 1,
            userId: contact.id,
            unseenMsgs: 0,
            chat: []
          })
        }
      })
    },
    setUserStatus: (state, action) => {
      state.profileUser = { ...state.profileUser, status: action.payload.status }
    },

    // 1) Mensagem do usuário
    addUserMessage: (state, action) => {
      const { msg } = action.payload
      const existingChat = state.chats.find(chat => chat.userId === state.activeUser?.id)
      if (!existingChat) return

      existingChat.chat.push({
        id: nanoid(),
        message: msg,
        time: new Date(),
        senderId: state.profileUser.id,
        msgStatus: { isSent: true, isDelivered: false, isSeen: false }
      })

      // Reordenar
      state.chats = state.chats.filter(c => c.userId !== state.activeUser?.id)
      state.chats.unshift(existingChat)
    },

    // 2) Placeholder do bot (spinner)
    addBotPlaceholder: (state, action) => {
      const { tempId } = action.payload
      const existingChat = state.chats.find(chat => chat.userId === state.activeUser?.id)
      if (!existingChat) return

      existingChat.chat.push({
        id: tempId, // importante: vamos atualizar por este id
        message: 'Digitando…', // texto provisório
        time: new Date(),
        senderId: 2,
        isLoading: true, // flag para UI (mostrar spinner)
        isError: false,
        msgStatus: { isSent: true, isDelivered: false, isSeen: false }
      })

      state.chats = state.chats.filter(c => c.userId !== state.activeUser?.id)
      state.chats.unshift(existingChat)
    },

    // 3) Atualiza o placeholder com resposta/erro
    updateBotMessage: (state, action) => {
      const { tempId, newMessage, isError = false } = action.payload
      const existingChat = state.chats.find(chat => chat.userId === state.activeUser?.id)
      if (!existingChat) return

      const msg = existingChat.chat.find(m => m.id === tempId)
      if (!msg) return

      msg.message = newMessage
      msg.isLoading = false
      msg.isError = isError
      msg.time = new Date()
      msg.msgStatus = { isSent: true, isDelivered: true, isSeen: false }

      state.chats = state.chats.filter(c => c.userId !== state.activeUser?.id)
      state.chats.unshift(existingChat)
    }
  }
})

// --- Thunk que encadeia tudo: usuário -> placeholder -> API -> update ---
export const sendMsgWithLLM = msg => async dispatch => {
  // adiciona mensagem do usuário
  dispatch(addUserMessage({ msg }))

  // cria placeholder do bot e guarda o id pra substituir depois
  const tempId = nanoid()
  dispatch(addBotPlaceholder({ tempId }))

  try {
    const res = await api.post('/chat/', { message: msg })
    const answer = res.data?.answer ?? ''
    dispatch(updateBotMessage({ tempId, newMessage: answer }))
  } catch (e) {
    dispatch(
      updateBotMessage({
        tempId,
        newMessage: 'Ops! Não consegui responder agora. Tente novamente.',
        isError: true
      })
    )
  }
}

export const uploadFileWithLLM = file => async dispatch => {
  const fileMsg = `📎 Enviou um arquivo: ${file?.name || 'arquivo'}`
  dispatch(addUserMessage({ msg: fileMsg }))

  const tempId = nanoid()
  dispatch(addBotPlaceholder({ tempId }))

  try {
    const formData = new FormData()
    formData.append('file', file)

    const res = await api.post('/chat/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // Tente extrair uma resposta amigável; caia em um padrão se não houver
    const answer = res.data?.answer

    dispatch(updateBotMessage({ tempId, newMessage: answer }))
  } catch (e) {
    dispatch(
      updateBotMessage({
        tempId,
        newMessage: 'Não consegui processar o arquivo agora. Tente novamente.',
        isError: true
      })
    )
  }
}

export const { getActiveUserData, addNewChat, setUserStatus, addUserMessage, addBotPlaceholder, updateBotMessage } =
  chatSlice.actions

export default chatSlice.reducer
