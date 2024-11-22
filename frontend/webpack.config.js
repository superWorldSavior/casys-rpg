const createExpoWebpackConfigAsync = require('@expo/webpack-config');
const path = require('path');

module.exports = async function (env, argv) {
  const config = await createExpoWebpackConfigAsync({
    ...env,
    babel: {
      dangerouslyAddBabelTransformInline: true,
    },
  }, argv);

  // Customize the webpack config
  config.resolve = {
    ...config.resolve,
    alias: {
      ...config.resolve.alias,
      'react-native$': 'react-native-web',
      'react-native-web': path.resolve(__dirname, 'node_modules/react-native-web'),
      '@': path.resolve(__dirname, 'src'),
    },
    extensions: [
      '.web.tsx',
      '.web.ts',
      '.web.jsx',
      '.web.js',
      '.tsx',
      '.ts',
      '.jsx',
      '.js',
      ...config.resolve.extensions,
    ],
    fallback: {
      ...config.resolve.fallback,
      "crypto": false,
      "stream": false,
      "path": false,
      "fs": false,
    },
  };

  // Configure development server
  if (config.devServer) {
    config.devServer = {
      ...config.devServer,
      port: 19007,
      host: '0.0.0.0',
      historyApiFallback: true,
      hot: true,
      client: {
        overlay: {
          errors: true,
          warnings: false,
        },
      },
    };
  }

  return config;
};
