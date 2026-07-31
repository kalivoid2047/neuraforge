import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@neuraforge/ui", "@neuraforge/viz-widgets"],
  experimental: {
    // TypeScript 7's native compiler doesn't expose the JS Compiler API
    // Next.js normally uses for its in-process build-time typecheck, so
    // `next build` shells out to the project-local `tsc` instead. Without
    // this, `next build` refuses to run at all under TS 7 with:
    // "TypeScript 7.0.2 does not provide the compiler API required by
    // Next.js." (docs/app/api-reference/config/next-config-js/useTypeScriptCli)
    useTypeScriptCli: true,
  },
};

export default nextConfig;
