import globals from 'globals';
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import stylistic from '@stylistic/eslint-plugin-ts';

export default [
	{ files: ['**/*.{js,mjs,cjs,ts}'] },
	{ languageOptions: { globals: globals.node } },
	{ plugins: { '@stylistic': stylistic } },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  stylistic.configs['disable-legacy'],
  {
    rules: {
      'import/no-unresolved': 'off',
      'no-process-env': 'off',
      'no-tabs': ['off'],
      quotes: ['error', 'single'],
      semi: ['error', 'always']
    },
  },
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
    },
  },
];
