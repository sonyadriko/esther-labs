'use client';

import { useState, useEffect } from 'react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { getVideoStatus, VideoStatusResponse } from '@/lib/api';

interface VideoStatusTrackerProps {
    videoId: string;
    onComplete: (status: VideoStatusResponse) => void;
    onError: (error: string) => void;
}

const STATUS_PROGRESS: Record<string, number> = {
    pending: 10,
    processing: 20,
    generating_script: 35,
    generating_audio: 55,
    generating_video: 80,
    done: 100,
    failed: 0,
};

const STATUS_LABELS: Record<string, string> = {
    pending: 'Menunggu...',
    processing: 'Memproses...',
    generating_script: 'Membuat Script Review',
    generating_audio: 'Membuat Voice Over',
    generating_video: 'Membuat Video',
    done: 'Selesai!',
    failed: 'Gagal',
};

export function VideoStatusTracker({ videoId, onComplete, onError }: VideoStatusTrackerProps) {
    const [status, setStatus] = useState<VideoStatusResponse | null>(null);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        const checkStatus = async () => {
            try {
                const result = await getVideoStatus(videoId);
                setStatus(result);
                setProgress(STATUS_PROGRESS[result.status] || 0);

                if (result.status === 'done') {
                    onComplete(result);
                } else if (result.status === 'failed') {
                    onError(result.error_message || 'Video generation failed');
                }
            } catch (error) {
                console.error('Error checking status:', error);
            }
        };

        // Initial check
        checkStatus();

        // Poll every 2 seconds until done or failed
        const interval = setInterval(() => {
            if (status?.status !== 'done' && status?.status !== 'failed') {
                checkStatus();
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [videoId, status?.status, onComplete, onError]);

    return (
        <Card className="w-full">
            <CardContent className="p-6 space-y-6">
                {/* Status Badge */}
                <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Status Video</h3>
                    <Badge
                        variant={
                            status?.status === 'done'
                                ? 'default'
                                : status?.status === 'failed'
                                    ? 'destructive'
                                    : 'secondary'
                        }
                    >
                        {STATUS_LABELS[status?.status || 'pending']}
                    </Badge>
                </div>

                {/* Progress Bar */}
                <div className="space-y-2">
                    <Progress value={progress} className="h-3" />
                    <p className="text-sm text-muted-foreground text-center">
                        {progress}% Complete
                    </p>
                </div>

                {/* Status Message */}
                {status?.progress_message && (
                    <p className="text-center text-muted-foreground">
                        {status.progress_message}
                    </p>
                )}

                {/* Processing Animation */}
                {status?.status && !['done', 'failed'].includes(status.status) && (
                    <div className="flex justify-center">
                        <div className="flex gap-1">
                            {[0, 1, 2].map((i) => (
                                <div
                                    key={i}
                                    className="w-3 h-3 bg-primary rounded-full animate-bounce"
                                    style={{ animationDelay: `${i * 0.15}s` }}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Error Message */}
                {status?.status === 'failed' && status.error_message && (
                    <div className="p-4 bg-red-50 dark:bg-red-950 rounded-lg text-red-600 dark:text-red-400 text-sm">
                        {status.error_message}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
