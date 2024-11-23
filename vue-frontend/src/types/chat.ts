export interface Message {
  id: string;
  contenu: string;
  estUtilisateur: boolean;
  timestamp: number;
}

export interface ChatState {
  messages: Message[];
  estEnChargement: boolean;
  vitesseLecture: number;
}

export interface ChatError {
  message: string;
  code?: number;
}
