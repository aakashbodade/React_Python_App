import js from '@eslint/js';

export default [
  {
    // Apply to all JavaScript and JSX files
    files: ['**/*.js', '**/*.jsx'],
    
    // Use recommended rules
    ...js.configs.recommended,
    
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      globals: {
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        // React Testing Library globals
        test: 'readonly',
        expect: 'readonly',
        // Node.js globals
        process: 'readonly',
        module: 'readonly',
        require: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    
    rules: {
      // Match your existing config
      'semi': ['error', 'always'],
      'quotes': ['error', 'double'],
      
      // Code quality rules
      'no-unused-vars': 'warn',
      'no-console': 'off',
      'no-debugger': 'warn',
      
      // Best practices
      'eqeqeq': ['error', 'always'],
      'no-var': 'error',
      'prefer-const': 'error',
      'no-undef': 'error',
    },
  },
  
  {
    // Ignore common directories
    ignores: [
      'node_modules/**',
      'dist/**',
      'build/**',
      '.git/**',
      'coverage/**',
      '*.min.js',
      'venv/**',
      '**/*.py',
      'public/**',
    ],
  },
];