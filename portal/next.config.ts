import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: process.env.NEXT_OUTPUT_EXPORT ? "export" : undefined,
  trailingSlash: process.env.NEXT_OUTPUT_EXPORT ? true : undefined,
  assetPrefix: process.env.NEXT_PUBLIC_ASSET_PREFIX || undefined,
  images: { unoptimized: true },
};

export default nextConfig;