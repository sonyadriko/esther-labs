'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProductForm } from '@/components/ProductForm';
import { createVideo } from '@/lib/api';

export default function HomePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: {
    productName: string;
    productDescription: string;
    style: string;
    images: File[];
  }) => {
    setIsLoading(true);
    setError(null);

    try {
      const video = await createVideo({
        productName: data.productName,
        productDescription: data.productDescription,
        style: data.style as 'luxury' | 'minimal' | 'tech' | 'lifestyle',
        images: data.images,
      });

      // Redirect to result page
      router.push(`/result/${video.id}`);
    } catch (err) {
      setError('Gagal membuat video. Silakan coba lagi.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-indigo-50 dark:from-gray-950 dark:via-gray-900 dark:to-violet-950">
      {/* Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-violet-400/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-indigo-400/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 right-1/3 w-80 h-80 bg-purple-400/20 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-violet-100 dark:bg-violet-900/30 rounded-full text-violet-600 dark:text-violet-400 text-sm font-medium mb-6">
            <span className="animate-pulse">🔥</span>
            <span>AI-Powered Video Generator</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-4">
            Buat Video Review Produk
            <span className="block bg-gradient-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent">
              Dalam Hitungan Detik
            </span>
          </h1>

          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Upload gambar produk, isi deskripsi, dan biarkan AI membuat video review profesional untuk TikTok, Reels, dan Ads.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12 max-w-4xl mx-auto">
          {[
            { icon: '🎬', title: 'Auto Script', desc: 'Script review otomatis' },
            { icon: '🎙️', title: 'Voice Over', desc: 'Suara natural AI' },
            { icon: '⚡', title: 'Instant Video', desc: 'Siap dalam detik' },
          ].map((feature) => (
            <div
              key={feature.title}
              className="flex items-center gap-3 p-4 bg-white/70 dark:bg-gray-800/70 backdrop-blur rounded-xl border border-gray-200/50 dark:border-gray-700/50"
            >
              <span className="text-2xl">{feature.icon}</span>
              <div>
                <div className="font-semibold">{feature.title}</div>
                <div className="text-sm text-muted-foreground">{feature.desc}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Form Section */}
        <div className="max-w-lg mx-auto">
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-2xl shadow-violet-500/10 border border-gray-200/50 dark:border-gray-700/50 p-6 md:p-8">
            {error && (
              <div className="mb-6 p-4 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
                {error}
              </div>
            )}

            <ProductForm onSubmit={handleSubmit} isLoading={isLoading} />
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-sm text-muted-foreground">
          <p>Video dibuat dengan AI • Gratis tanpa watermark</p>
        </div>
      </div>
    </main>
  );
}
