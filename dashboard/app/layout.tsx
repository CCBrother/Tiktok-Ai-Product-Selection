import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI产品雷达",
  description: "TikTok Shop US viral product radar"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
