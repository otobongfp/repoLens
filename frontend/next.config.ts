import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  devIndicators: false,
  webpack: (config, { isServer }) => {
    // disable webpack caching to prevent large cache files
    config.cache = false;

    // Remove cache-related plugins
    config.plugins = config.plugins?.filter((plugin: any) => {
      const pluginName = plugin.constructor.name;
      return !pluginName.includes('Cache') && !pluginName.includes('cache');
    });

    return config;
  },
  // exclude from build output
  outputFileTracingExcludes: {
    '*': [
      'cache/**/*',
      '**/cache/**/*',
      'node_modules/@swc/core/**/*',
      'node_modules/webpack/**/*',
      '.next/cache/**/*',
    ],
  },
  // Disable build caching
  experimental: {
    webpackBuildWorker: false,
  },
};

export default nextConfig;
