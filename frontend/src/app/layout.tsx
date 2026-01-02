import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Video Generator - Buat Video Review Produk Otomatis",
  description: "Generate video review produk dengan AI untuk TikTok, Reels, dan Ads. Upload gambar, isi deskripsi, dapatkan video profesional dalam hitungan detik.",
  keywords: ["AI video generator", "video review produk", "TikTok", "Reels", "marketing video", "product review"],
  authors: [{ name: "EstherLabs" }],
  openGraph: {
    title: "AI Video Generator - Video Review Produk Otomatis",
    description: "Generate video review produk dengan AI untuk TikTok, Reels, dan Ads.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
