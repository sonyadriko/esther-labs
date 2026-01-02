const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface VideoRequest {
    productName: string;
    productDescription: string;
    style: 'luxury' | 'minimal' | 'tech' | 'lifestyle';
    images: File[];
}

export interface VideoResponse {
    id: string;
    product_name: string;
    product_description: string | null;
    style: string;
    status: string;
    script: string | null;
    audio_url: string | null;
    video_url: string | null;
    thumbnail_url: string | null;
    error_message: string | null;
    created_at: string;
    updated_at: string;
}

export interface VideoStatusResponse {
    id: string;
    status: string;
    video_url: string | null;
    error_message: string | null;
    progress_message: string;
}

export async function createVideo(data: VideoRequest): Promise<VideoResponse> {
    const formData = new FormData();
    formData.append('product_name', data.productName);
    formData.append('product_description', data.productDescription);
    formData.append('style', data.style);

    data.images.forEach((image) => {
        formData.append('images', image);
    });

    const response = await fetch(`${API_BASE_URL}/api/videos`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('Failed to create video');
    }

    return response.json();
}

export async function getVideo(videoId: string): Promise<VideoResponse> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}`);

    if (!response.ok) {
        throw new Error('Failed to get video');
    }

    return response.json();
}

export async function getVideoStatus(videoId: string): Promise<VideoStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}/status`);

    if (!response.ok) {
        throw new Error('Failed to get video status');
    }

    return response.json();
}

export function getVideoDownloadUrl(videoId: string): string {
    return `${API_BASE_URL}/api/videos/${videoId}/download`;
}

export function getVideoStreamUrl(videoPath: string): string {
    // Extract filename from path if needed
    const filename = videoPath.split('/').pop();
    return `${API_BASE_URL}/outputs/${filename}`;
}
