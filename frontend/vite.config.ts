import {defineConfig, loadEnv} from 'vite';
import react from '@vitejs/plugin-react';
import svgr from 'vite-plugin-svgr';
import eslint from 'vite-plugin-eslint';
import path from 'path';
import checker from 'vite-plugin-checker';

// https://vitejs.dev/config/
export default defineConfig(({mode}) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@styles': path.resolve(__dirname, './src/app/styles'),
        '@shared': path.resolve(__dirname, './src/shared'),
      },
    },
    define: {
      'process.env': env,
    },
    server: {port: 3000},
    plugins: [
      react(),
      svgr({
        include: '**/*.svg?react',
      }),
      eslint({cache: true, failOnWarning: false, emitWarning: false}),
      checker({
        typescript: true,
      }),
    ],
    build: {
      outDir: './build',
    },
  };
});
