import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';
import { jsx } from 'react/jsx-runtime';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  ...compat.configs({
    extends: [
      'next',
      'next/typescript',
      'next/core-web-vitals',
      'plugin:prettier/recommended',
    ],
    plugins: ['prettier'],
    rules: {
      // TODO turn off use of any temporarily
      '@typescript-eslint/no-explicit-any': 'off',
      'react/react-in-jsx-scope': 'off',
    },
  }),
];

export default eslintConfig;
