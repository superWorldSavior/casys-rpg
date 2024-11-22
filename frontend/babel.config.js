module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      'react-native-reanimated/plugin',
      'nativewind/babel',
      'babel-plugin-react-native-web',
      '@babel/plugin-proposal-export-namespace-from',
      ['module-resolver', {
        root: ['.'],
        alias: {
          '@': './src',
        },
        extensions: [
          '.web.tsx',
          '.web.ts',
          '.web.jsx',
          '.web.js',
          '.ios.tsx',
          '.ios.ts',
          '.android.tsx',
          '.android.ts',
          '.tsx',
          '.ts',
          '.jsx',
          '.js',
          '.json',
        ],
      }],
    ],
  };
};
