"""Groq API integration for tarot readings"""

import random
from groq import Groq
from bot.config import settings
from bot.core.card_texts import CARD_TEXTS

client = Groq(api_key=settings.GROQ_API_KEY)


async def generate_tarot_reading(
    scenario_name: str,
    problem_text: str,
    cards: list,
    spread_type: str = "three_cards",
    position_names: list = None
) -> str:
    """Generate a tarot reading using Groq API."""
    
    # Prepare cards info
    cards_info = []
    for i, card in enumerate(cards):
        status = "перевёрнутая" if card.is_reversed else "прямая"
        card_data = CARD_TEXTS.get(card.card_id, {})
        general_variants = card_data.get("general", [])
        if general_variants:
            card_text = random.choice(general_variants)
        else:
            card_text = "Значение карты"
        
        # Если есть названия позиций — используем их
        pos_name = position_names[i] if position_names and i < len(position_names) else f"Карта {i+1}"
        cards_info.append(f"{pos_name} — {card.name_ru} ({status})")
        cards_info.append(f"{card_text}")
        cards_info.append("")  # пустая строка для разделения
    
    cards_text = "\n".join(cards_info)
    
    # Определяем количество карт для инструкции
    if spread_type == "one_card":
        format_instruction = """
Для расклада на одну карту используй формат:

**Совет** — {название карты} ({прямая/перевёрнутая})
(2 предложения разбора)
"""
    elif spread_type == "two_cards":
        format_instruction = """
Для расклада на две карты используй формат:

**1. Корень проблемы** — {название карты} ({прямая/перевёрнутая})
(2 предложения разбора)

**2. Решение** — {название карты} ({прямая/перевёрнутая})
(2 предложения разбора)
"""
    else:
        format_instruction = """
Для расклада на три карты используй формат:

**1. Ситуация сейчас** — {название карты} ({прямая/перевёрнутая})
(2 предложения разбора)

**2. Препятствие** — {название карты} ({прямая/перевёрнутая})
(2 предложения разбора)

**3. Итог** — {название карты} ({прямая/перевёрнутая})
(2 предложения разбора)
"""
    
    prompt = f"""Ты — опытный таролог. Дай структурированное толкование расклада Таро.

Ситуация пользователя: {problem_text}

Расклад: {scenario_name}

Карты:
{cards_text}

{format_instruction}

В конце обязательно напиши **Общий итог и совет:** — 2-3 предложения, которые подводят итог всему раскладу.

Важно:
- Не пропускай ни одну карту
- Каждая карта должна быть разобрана отдельно
- Используй жирное выделение для заголовков
- Пиши кратко, но содержательно

Теперь напиши своё толкование в этом формате:"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты — мудрый таролог. Отвечаешь строго в заданном формате. Используешь жирное выделение для заголовков. Завершаешь общим итогом и советом."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        text = response.choices[0].message.content
        print(f"🔍 Groq токенов: {response.usage.completion_tokens}")
        return text.strip()
        
    except Exception as e:
        print(f"Groq API error: {e}")
        return _get_fallback_text(cards, spread_type, position_names)


def _get_fallback_text(cards: list, spread_type: str, position_names: list = None) -> str:
    """Fallback text if API fails"""
    if spread_type == "one_card":
        card = cards[0]
        status = " (перевёрнутая)" if card.is_reversed else ""
        return f"🃏 {card.name_ru}{status}\n\n{card.short_upright if not card.is_reversed else card.short_reversed}"
    else:
        text = "✨ Ваш расклад:\n\n"
        for i, card in enumerate(cards):
            status = "⚠️ перевёрнутая" if card.is_reversed else "✨ прямая"
            pos_name = position_names[i] if position_names and i < len(position_names) else f"Карта {i+1}"
            text += f"**{pos_name}** — {card.name_ru} ({status})\n"
            text += f"{card.short_upright if not card.is_reversed else card.short_reversed}\n\n"
        return text