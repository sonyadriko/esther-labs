'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { getVideoDownloadUrl, getVideoStreamUrl, VideoResponse } from '@/lib/api';

interface VideoPlayerProps {
    video: VideoResponse;
    onCreateNew: () => void;
}

export function VideoPlayer({ video, onCreateNew }: VideoPlayerProps) {
    const videoUrl = video.video_url ? getVideoStreamUrl(video.video_url) : '';
    const downloadUrl = getVideoDownloadUrl(video.id);

    return (
        <Card className="w-full overflow-hidden">
            <CardContent className="p-0">
                {/* Video Player */}
                <div className="relative aspect-[9/16] max-h-[500px] bg-black">
                    {videoUrl ? (
                        <video
                            src={videoUrl}
                            controls
                            autoPlay
                            loop
                            className="w-full h-full object-contain"
                        />
                    ) : (
                        <div className="absolute inset-0 flex items-center justify-center text-white">
                            Video tidak tersedia
                        </div>
                    )}
                </div>

                {/* Video Info & Actions */}
                <div className="p-6 space-y-6">
                    {/* Product Info */}
                    <div>
                        <h3 className="text-xl font-semibold">{video.product_name}</h3>
                        {video.product_description && (
                            <p className="text-muted-foreground mt-1 line-clamp-2">
                                {video.product_description}
                            </p>
                        )}
                    </div>

                    {/* Script Preview */}
                    {video.script && (
                        <div className="p-4 bg-muted rounded-lg">
                            <h4 className="text-sm font-semibold mb-2">Script:</h4>
                            <p className="text-sm text-muted-foreground">{video.script}</p>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-3">
                        <Button
                            asChild
                            className="flex-1 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
                        >
                            <a href={downloadUrl} download>
                                ⬇️ Download Video
                            </a>
                        </Button>
                        <Button
                            variant="outline"
                            className="flex-1"
                            onClick={onCreateNew}
                        >
                            🎬 Buat Video Baru
                        </Button>
                    </div>

                    {/* Share Options */}
                    <div className="text-center">
                        <p className="text-sm text-muted-foreground">
                            Video siap untuk TikTok, Reels, atau Ads ✨
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
