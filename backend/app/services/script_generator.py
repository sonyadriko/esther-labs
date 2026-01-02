"""
Script Generator Service
Uses Gemini API to generate product review scripts.
"""
import google.generativeai as genai
from app.core.config import get_settings

settings = get_settings()


class ScriptGenerator:
    """Generate product review scripts using LLM."""
    
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    async def generate_script(
        self, 
        product_name: str, 
        product_description: str,
        style: str = "minimal"
    ) -> dict:
        """
        Generate a product review script.
        
        Returns:
            dict with 'hook', 'benefits', 'cta' sections
        """
        style_prompts = {
            "luxury": "mewah, eksklusif, dan premium",
            "minimal": "simpel, bersih, dan modern", 
            "tech": "inovatif, canggih, dan futuristik",
            "lifestyle": "casual, friendly, dan relatable"
        }
        
        style_desc = style_prompts.get(style, style_prompts["minimal"])
        
        prompt = f"""Kamu adalah copywriter profesional untuk video review produk pendek (10-30 detik).
        
Buat script review untuk produk berikut:
- Nama Produk: {product_name}
- Deskripsi: {product_description or 'Tidak ada deskripsi'}
- Gaya: {style_desc}

Format output (dalam Bahasa Indonesia):

HOOK:
[1 kalimat pembuka yang menarik perhatian, maksimal 10 kata]

BENEFITS:
[2-3 kalimat tentang manfaat utama produk, maksimal 30 kata total]

CTA:
[1 kalimat call to action, maksimal 10 kata]

Pastikan script terdengar natural untuk diucapkan dan cocok untuk video TikTok/Reels."""

        if self.model:
            try:
                response = await self.model.generate_content_async(prompt)
                return self._parse_script(response.text)
            except Exception as e:
                print(f"Error generating script: {e}")
                return self._get_fallback_script(product_name)
        else:
            return self._get_fallback_script(product_name)
    
    def _parse_script(self, text: str) -> dict:
        """Parse the generated script into sections."""
        sections = {
            "hook": "",
            "benefits": "",
            "cta": "",
            "full_script": ""
        }
        
        current_section = None
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith("HOOK"):
                current_section = "hook"
                continue
            elif line.upper().startswith("BENEFITS") or line.upper().startswith("BENEFIT"):
                current_section = "benefits"
                continue
            elif line.upper().startswith("CTA"):
                current_section = "cta"
                continue
            
            if current_section and line:
                if sections[current_section]:
                    sections[current_section] += " " + line
                else:
                    sections[current_section] = line
        
        # Create full script
        sections["full_script"] = f"{sections['hook']} {sections['benefits']} {sections['cta']}"
        
        return sections
    
    def _get_fallback_script(self, product_name: str) -> dict:
        """Fallback script when API is not available."""
        return {
            "hook": f"Produk ini hadir untuk kamu yang mencari solusi praktis!",
            "benefits": f"{product_name} menawarkan kualitas terbaik dengan desain yang elegan. Cocok untuk kebutuhan sehari-hari.",
            "cta": "Yuk, dapatkan sekarang sebelum kehabisan!",
            "full_script": f"Produk ini hadir untuk kamu yang mencari solusi praktis! {product_name} menawarkan kualitas terbaik dengan desain yang elegan. Cocok untuk kebutuhan sehari-hari. Yuk, dapatkan sekarang sebelum kehabisan!"
        }


# Singleton instance
script_generator = ScriptGenerator()
