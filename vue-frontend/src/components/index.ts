// Import des composants par domaine
import * as auth from './auth'
import * as book from './book'
import * as chat from './features/chat'
import * as common from './common'
import * as layout from './layout'
import * as reader from './reader'
import * as ui from './ui'

// Export des composants par domaine
export {
  auth,
  book,
  chat,
  common,
  layout,
  reader,
  ui
}

// Export par défaut de tous les composants
export default {
  ...auth,
  ...book,
  ...chat,
  ...common,
  ...layout,
  ...reader,
  ...ui
}
