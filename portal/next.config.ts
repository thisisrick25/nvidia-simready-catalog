import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: process.env.NEXT_OUTPUT_EXPORT ? "export" : undefined,
  trailingSlash: process.env.NEXT_OUTPUT_EXPORT ? true : undefined,
  images: { unoptimized: true },
};

export default nextConfig;