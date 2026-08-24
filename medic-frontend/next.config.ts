import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const waUrl = process.env.NEXT_PUBLIC_WHATSAPP_SERVICE_URL || "http://localhost:8001";
    return [
      {
        source: "/api/whatsapp/:path*",
        destination: `${waUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
