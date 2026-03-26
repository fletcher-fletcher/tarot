"""Spread image renderer using Pillow"""

import os
import time
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

from bot.config import settings
from bot.core.cards_data import TarotCard


class SpreadRenderer:
    """Spread image renderer using Pillow"""
    
    def __init__(self):
        self.card_width = 220      # Увеличено
        self.card_height = 385     # Увеличено
        self.spacing = 25          # Увеличено
        self.padding = 60          # Увеличено
        
        self.temp_dir = settings.TEMP_DIR
        self.backgrounds_dir = settings.BACKGROUNDS_DIR
        self.fonts_dir = settings.FONTS_DIR
        self.cards_dir = settings.CARDS_DIR
        
        self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts (оставлено для возможного будущего использования)"""
        self.title_font = None
        self.label_font = None
        
        try:
            playfair_path = self.fonts_dir / "playfair.ttf"
            opensans_path = self.fonts_dir / "opensans.ttf"
            
            if playfair_path.exists():
                self.title_font = ImageFont.truetype(str(playfair_path), 28)
            if opensans_path.exists():
                self.label_font = ImageFont.truetype(str(opensans_path), 16)
        except Exception as e:
            logger.warning(f"Font loading failed: {e}")
        
        if not self.title_font:
            self.title_font = ImageFont.load_default()
        if not self.label_font:
            self.label_font = ImageFont.load_default()
    
    def _load_background(self, spread_id: str, width: int, height: int) -> Image.Image:
        """Load universal background"""
        bg_path = self.backgrounds_dir / "default.jpg"
        
        if bg_path.exists():
            bg = Image.open(bg_path)
            bg = bg.resize((width, height))
            return bg
        
        # Фон по умолчанию
        bg = Image.new('RGB', (width, height), color='#0a0a1a')
        draw = ImageDraw.Draw(bg)
        
        for i in range(height):
            ratio = i / height
            color = (
                int(10 + 30 * ratio),
                int(10 + 20 * ratio),
                int(26 + 40 * ratio)
            )
            draw.line([(0, i), (width, i)], fill=color)
        
        return bg
    
    async def create_spread_image(
        self,
        spread_name: str,
        spread_id: str,
        cards: List[Tuple[TarotCard, dict]],
        question: Optional[str] = None,
        total_meaning: Optional[str] = None
    ) -> str:
        """Create spread image with ONLY cards — no text"""
        num_cards = len(cards)
        
        # Рассчитываем размеры (только карты, без текста)
        cards_row_width = num_cards * (self.card_width + self.spacing) - self.spacing
        total_width = max(cards_row_width + 2 * self.padding, 700)
        total_height = self.card_height + 2 * self.padding
        
        # Создаём фон
        background = self._load_background(spread_id, total_width, total_height)
        
        # Размещаем карты
        start_x = (total_width - (num_cards * (self.card_width + self.spacing) - self.spacing)) // 2
        cards_y = self.padding
        
        for i, (card, position) in enumerate(cards):
            x = start_x + i * (self.card_width + self.spacing)
            
            # Загружаем карту
            card_path = self.cards_dir / f"{card.card_id}.jpg"
            if card_path.exists():
                card_img = Image.open(card_path)
                card_img = card_img.resize((self.card_width, self.card_height))
            else:
                card_img = Image.new('RGB', (self.card_width, self.card_height), color='#333344')
                card_draw = ImageDraw.Draw(card_img)
                card_draw.text((10, self.card_height // 2), "Card not found", fill='#ffffff')
            
            # Переворачиваем, если нужно
            if card.is_reversed:
                card_img = card_img.rotate(180)
            
            # Добавляем рамку
            border_width = 3
            bordered_card = Image.new('RGB', (
                self.card_width + border_width * 2,
                self.card_height + border_width * 2
            ), color='#c9a87b')
            bordered_card.paste(card_img, (border_width, border_width))
            
            background.paste(bordered_card, (x - border_width, cards_y - border_width))
        
        # Сохраняем
        filename = f"spread_{spread_id}_{int(time.time())}.png"
        output_path = self.temp_dir / filename
        background.save(str(output_path), "PNG")
        
        return str(output_path)


spread_renderer = SpreadRenderer()