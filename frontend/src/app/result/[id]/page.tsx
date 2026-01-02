'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { VideoStatusTracker } from '@/components/VideoStatusTracker';
import { VideoPlayer } from '@/components/VideoPlayer';
import { Button } from '@/components/ui/button';
import { getVideo, VideoResponse, VideoStatusResponse } from '@/lib/api';

interface ResultPageProps {
    params: Promise<{ id: string }>;
}

export default function ResultPage({ params }: ResultPageProps) {
    const router = useRouter();
    const [videoId, setVideoId] = useState<string | null>(null);
    const [video, setVideo] = useState<VideoResponse | null>(null);
    const [isComplete, setIsComplete] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        params.then((p) => setVideoId(p.id));
    }, [params]);

    useEffect(() => {
        if (videoId) {
            getVideo(videoId)
                .then((v) => {
                    setVideo(v);
                    if (v.status === 'done') {
                        setIsComplete(true);
                    } else if (v.status === 'failed') {
                        setError(v.error_message || 'Video generation failed');
                    }
                })
                .catch((err) => {
                    console.error(err);
                    setError('Failed to load video');
                });
        }
    }, [videoId]);

    const handleComplete = useCallback(async (status: VideoStatusResponse) => {
        if (videoId) {
            const updatedVideo = await getVideo(videoId);
            setVideo(updatedVideo);
            setIsComplete(true);
        }
    }, [videoId]);

    const handleError = useCallback((errorMessage: string) => {
        setError(errorMessage);
    }, []);

    const handleCreateNew = () => {
        router.push('/');
    };

    if (!videoId) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-indigo-50 dark:from-gray-950 dark:via-gray-900 dark:to-violet-950">
            {/* Background Elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-violet-400/20 rounded-full blur-3xl" />
                <div className="absolute top-1/2 -left-40 w-80 h-80 bg-indigo-400/20 rounded-full blur-3xl" />
            </div>

            <div className="relative z-10 container mx-auto px-4 py-12">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
                        {isComplete ? '🎉 Video Siap!' : '⏳ Sedang Membuat Video...'}
                    </h1>
                    {video && (
                        <p className="text-muted-foreground mt-2">
                            {video.product_name}
                        </p>
                    )}
                </div>

                {/* Content */}
                <div className="max-w-lg mx-auto">
                    {error ? (
                        <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-xl p-6 text-center">
                            <div className="text-5xl mb-4">😢</div>
                            <h2 className="text-xl font-semibold mb-2">Terjadi Kesalahan</h2>
                            <p className="text-muted-foreground mb-6">{error}</p>
                            <Button onClick={handleCreateNew}>
                                Coba Lagi
                            </Button>
                        </div>
                    ) : isComplete && video ? (
                        <VideoPlayer video={video} onCreateNew={handleCreateNew} />
                    ) : (
                        <VideoStatusTracker
                            videoId={videoId}
                            onComplete={handleComplete}
                            onError={handleError}
                        />
                    )}
                </div>

                {/* Back Button */}
                {!isComplete && !error && (
                    <div className="text-center mt-8">
                        <Button variant="ghost" onClick={handleCreateNew}>
                            ← Kembali ke Home
                        </Button>
                    </div>
                )}
            </div>
        </main>
    );
}
