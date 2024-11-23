import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Message {
  id: string
  contenu: string
  estUtilisateur: boolean
  timestamp: number
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const estEnChargement = ref(false)
  const vitesseLecture = ref(50) // Vitesse de lecture par défaut (ms par caractère)

  function ajouterMessage(contenu: string, estUtilisateur: boolean = true) {
    console.debug('[ChatStore] Ajout message:', { contenu, estUtilisateur })
    const message: Message = {
      id: crypto.randomUUID(),
      contenu,
      estUtilisateur,
      timestamp: Date.now()
    }
    messages.value.push(message)
  }

  function effacerHistorique() {
    console.debug('[ChatStore] Effacement historique')
    messages.value = []
  }

  function setVitesseLecture(vitesse: number) {
    console.debug('[ChatStore] Mise à jour vitesse lecture:', vitesse)
    vitesseLecture.value = Math.max(10, Math.min(200, vitesse))
  }

  async function envoyerMessageAI(message: string) {
    console.debug('[ChatStore] Envoi message AI:', message)
    estEnChargement.value = true
    try {
      ajouterMessage(message, true)
      
      // Appel à l'API backend
      const response = await fetch('/api/books/test_book.pdf/sections/1', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération de la section')
      }
      
      const data = await response.json()
      const reponse = data.section.content
      ajouterMessage(reponse, false)
    } catch (erreur) {
      console.error("[ChatStore] Erreur d'envoi du message:", erreur)
      ajouterMessage("Une erreur est survenue lors de la communication avec l'AI.", false)
      throw erreur
    } finally {
      estEnChargement.value = false
    }
  }

  return {
    messages,
    estEnChargement,
    vitesseLecture,
    ajouterMessage,
    effacerHistorique,
    setVitesseLecture,
    envoyerMessageAI
  }
}, {
  persist: true
})
