'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';

interface ProductFormProps {
    onSubmit: (data: {
        productName: string;
        productDescription: string;
        style: string;
        images: File[];
    }) => void;
    isLoading?: boolean;
}

const VIDEO_STYLES = [
    {
        id: 'luxury',
        name: 'Luxury',
        description: 'Mewah & Premium',
        emoji: '✨',
        gradient: 'from-amber-500 to-yellow-600'
    },
    {
        id: 'minimal',
        name: 'Minimal',
        description: 'Simpel & Modern',
        emoji: '🎯',
        gradient: 'from-gray-600 to-gray-800'
    },
    {
        id: 'tech',
        name: 'Tech',
        description: 'Futuristik & Canggih',
        emoji: '🚀',
        gradient: 'from-cyan-500 to-blue-600'
    },
    {
        id: 'lifestyle',
        name: 'Lifestyle',
        description: 'Casual & Friendly',
        emoji: '🌿',
        gradient: 'from-green-500 to-emerald-600'
    },
];

export function ProductForm({ onSubmit, isLoading }: ProductFormProps) {
    const [productName, setProductName] = useState('');
    const [productDescription, setProductDescription] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('minimal');
    const [images, setImages] = useState<File[]>([]);
    const [previews, setPreviews] = useState<string[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        if (files.length > 0) {
            // Limit to 3 images
            const newImages = [...images, ...files].slice(0, 3);
            setImages(newImages);

            // Create previews
            const newPreviews = newImages.map(file => URL.createObjectURL(file));
            setPreviews(prev => {
                // Cleanup old previews
                prev.forEach(url => URL.revokeObjectURL(url));
                return newPreviews;
            });
        }
    };

    const removeImage = (index: number) => {
        setImages(prev => prev.filter((_, i) => i !== index));
        setPreviews(prev => {
            URL.revokeObjectURL(prev[index]);
            return prev.filter((_, i) => i !== index);
        });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!productName.trim()) return;

        onSubmit({
            productName,
            productDescription,
            style: selectedStyle,
            images,
        });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-8">
            {/* Image Upload */}
            <div className="space-y-3">
                <Label className="text-base font-semibold">Gambar Produk</Label>
                <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center cursor-pointer hover:border-primary hover:bg-primary/5 transition-all duration-300"
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handleImageChange}
                        className="hidden"
                    />
                    <div className="space-y-2">
                        <div className="text-4xl">📸</div>
                        <p className="text-muted-foreground">
                            Klik untuk upload gambar produk
                        </p>
                        <p className="text-sm text-muted-foreground">
                            Maksimal 3 gambar (JPG, PNG)
                        </p>
                    </div>
                </div>

                {/* Image Previews */}
                {previews.length > 0 && (
                    <div className="grid grid-cols-3 gap-3 mt-4">
                        {previews.map((preview, index) => (
                            <div key={index} className="relative group">
                                <img
                                    src={preview}
                                    alt={`Preview ${index + 1}`}
                                    className="w-full h-24 object-cover rounded-lg border"
                                />
                                <button
                                    type="button"
                                    onClick={() => removeImage(index)}
                                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    ×
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Product Name */}
            <div className="space-y-3">
                <Label htmlFor="productName" className="text-base font-semibold">
                    Nama Produk *
                </Label>
                <Input
                    id="productName"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="Contoh: iPhone 15 Pro Max"
                    className="h-12 text-base"
                    required
                />
            </div>

            {/* Product Description */}
            <div className="space-y-3">
                <Label htmlFor="productDescription" className="text-base font-semibold">
                    Deskripsi & Keunggulan
                </Label>
                <Textarea
                    id="productDescription"
                    value={productDescription}
                    onChange={(e) => setProductDescription(e.target.value)}
                    placeholder="Jelaskan keunggulan dan fitur utama produk..."
                    className="min-h-[120px] text-base resize-none"
                />
            </div>

            {/* Video Style */}
            <div className="space-y-3">
                <Label className="text-base font-semibold">Gaya Video</Label>
                <div className="grid grid-cols-2 gap-3">
                    {VIDEO_STYLES.map((style) => (
                        <Card
                            key={style.id}
                            className={`cursor-pointer transition-all duration-300 hover:scale-[1.02] ${selectedStyle === style.id
                                    ? 'ring-2 ring-primary ring-offset-2'
                                    : 'hover:shadow-lg'
                                }`}
                            onClick={() => setSelectedStyle(style.id)}
                        >
                            <CardContent className="p-4 text-center">
                                <div className="text-2xl mb-1">{style.emoji}</div>
                                <div className="font-semibold">{style.name}</div>
                                <div className="text-xs text-muted-foreground">
                                    {style.description}
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>

            {/* Submit Button */}
            <Button
                type="submit"
                size="lg"
                className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 shadow-lg shadow-violet-500/25"
                disabled={isLoading || !productName.trim()}
            >
                {isLoading ? (
                    <span className="flex items-center gap-2">
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Memproses...
                    </span>
                ) : (
                    <span className="flex items-center gap-2">
                        🎬 Generate Video
                    </span>
                )}
            </Button>
        </form>
    );
}
