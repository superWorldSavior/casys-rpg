import { AppRegistry, Platform } from 'react-native';
import { createRoot } from 'react-dom/client';
import App from './App';

if (Platform.OS === 'web') {
  const rootTag = document.getElementById('root');
  AppRegistry.runApplication('Solo RPG AI Narrator', {
    rootTag: createRoot(rootTag),
    initialProps: {},
  });
} else {
  AppRegistry.registerComponent('Solo RPG AI Narrator', () => App);
}
