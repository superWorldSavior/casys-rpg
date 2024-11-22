import { defineStore } from 'pinia'

export interface Message {
  id: string
  contenu: string
  estUtilisateur: boolean
  timestamp: number
}

interface ChatState {
  messages: Message[]
  estEnChargement: boolean
  vitesseLecture: number
}

export const useChatStore = defineStore('chat', {
  state: (): ChatState => ({
    messages: [] as Message[],
    estEnChargement: false,
    vitesseLecture: 50 // Vitesse de lecture par défaut (ms par caractère)
  }),
  
  actions: {
    ajouterMessage(contenu: string, estUtilisateur: boolean = true) {
      const message: Message = {
        id: crypto.randomUUID(),
        contenu,
        estUtilisateur,
        timestamp: Date.now()
      }
      this.messages.push(message)
    },

    effacerHistorique() {
      this.messages = []
    },

    setVitesseLecture(vitesse: number) {
      this.vitesseLecture = Math.max(10, Math.min(200, vitesse))
    },

    async envoyerMessageAI(message: string) {
      this.estEnChargement = true
      try {
        this.ajouterMessage(message, true)
        // TODO: Integrate with AI backend
        const reponse = "Réponse temporaire de l'AI..." // Placeholder
        this.ajouterMessage(reponse, false)
      } catch (erreur) {
        console.error("Erreur d'envoi du message:", erreur)
      } finally {
        this.estEnChargement = false
      }
    }
  },

  persist: {
    enabled: true
  }
})
