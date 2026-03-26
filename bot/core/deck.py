import random
from typing import Optional, List
from bot.core.cards_data import CARDS_DB, TarotCard


def get_card_by_id(card_id: str) -> Optional[TarotCard]:
    """Get card by ID"""
    return CARDS_DB.get(card_id)


def get_all_cards() -> List[TarotCard]:
    """Get all cards"""
    return list(CARDS_DB.values())


def get_all_card_ids() -> List[str]:
    """Get all card IDs"""
    return list(CARDS_DB.keys())


def get_random_card(reversed_allowed: bool = True) -> TarotCard:
    """Get random card"""
    card_id = random.choice(list(CARDS_DB.keys()))
    card = CARDS_DB[card_id]
    
    # Create a copy with reversed flag
    is_reversed = reversed_allowed and random.random() < 0.3
    
    class CardWithReversed(TarotCard):
        pass
    
    new_card = CardWithReversed(
        card_id=card.card_id,
        name_ru=card.name_ru,
        name_en=card.name_en,
        arcana=card.arcana,
        number=card.number,
        short_upright=card.short_upright,
        short_reversed=card.short_reversed,
        keywords_upright=card.keywords_upright,
        keywords_reversed=card.keywords_reversed,
        meaning_upright=card.meaning_upright,
        meaning_reversed=card.meaning_reversed,
        advice=card.advice,
        warning=card.warning,
        description=card.description,
        image=card.image,
    )
    new_card.is_reversed = is_reversed
    
    return new_card


def get_multiple_cards(count: int, reversed_allowed: bool = True) -> List[TarotCard]:
    """Get multiple random cards"""
    return [get_random_card(reversed_allowed) for _ in range(count)]