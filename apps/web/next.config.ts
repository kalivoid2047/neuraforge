import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@neuraforge/ui", "@neuraforge/viz-widgets"],
};

export default nextConfig;
