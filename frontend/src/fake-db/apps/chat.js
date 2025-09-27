const previousDay = new Date(new Date().getTime() - 24 * 60 * 60 * 1000)
const dayBeforePreviousDay = new Date(new Date().getTime() - 24 * 60 * 60 * 1000 * 2)

export const db = {
  profileUser: {
    id: 1,
    avatar: '/images/avatars/1.png',
    fullName: 'John Doe',
    role: 'Admin',
    about:
      'Dessert chocolate cake lemon drops jujubes. Biscuit cupcake ice cream bear claw brownie brownie marshmallow.',
    status: 'online',
    settings: {
      isTwoStepAuthVerificationEnabled: true,
      isNotificationsOn: false
    }
  },
  contacts: [
    {
      id: 2,
      fullName: 'Aura',
      role: 'Assistente Virtual',
      about: '',
      avatar: '/images/avatars/2.png',
      status: 'online'
    }
  ],
  chats: [
    {
      id: 1,
      userId: 2,
      unseenMsgs: 1,
      chat: [
        {
          message: 'Olá! Como posso ajudar?',
          time: 'Mon Dec 10 2018 07:45:23 GMT+0000 (GMT)',
          senderId: 2
        }
      ]
    }
  ]
}
