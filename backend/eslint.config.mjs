/* eslint-disable import/no-anonymous-default-export */
import globals from 'globals';
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import shopifyEslintPlugin from '@shopify/eslint-plugin';
import stylistic from '@stylistic/eslint-plugin-ts';

export default [
	{ files: ['**/*.{js,mjs,cjs,ts}'] },
	{ languageOptions: { globals: globals.node } },
	{ plugins: { '@stylistic': stylistic } },
  stylistic.configs['disable-legacy'],
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  ...shopifyEslintPlugin.configs.esnext,
  {
    rules: {
      'import/no-unresolved': 'off',
      'no-process-env': 'off',
      '@babel/object-curly-spacing': ['error', 'always'],
      'no-tabs': ['off'],
      quotes: ['error', 'single'],
    },
  },
  {
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
    },
  },
];
