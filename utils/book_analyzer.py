"""
Book Analyzer module for extracting key information from text files.

This module provides functions to analyze text content from books,
extracting characters, places, synopsis, and interesting passages.
"""
import re
import os
import random
from collections import Counter
from typing import List, Dict, Any, Set, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Load common words to filter out from characters list
COMMON_WORDS_PATH = os.path.join(os.path.dirname(__file__), "data", "dict")

# Interesting keywords for synopsis extraction
INTERESTING_KEYWORDS = {
    "bet", "wager", "gamble", "pray", "suicide", "kill", "catch", "oust", "coup",
    "death", "crash", "died", "rape", "die", "murder", "jail", "assault", "lost",
    "battle", "hit", "strike", "shoot", "fight", "bleed", "stab", "burn", "kiss",
    "celebrate", "overcome", "surrender", "yell", "shout", "escape", "sex",
    "negotiation", "deal", "court", "marry", "married", "divorce", "divorced",
    "desperate", "loser", "victory", "defeat", "succeed", "fail", "betray",
    "love", "hate", "discover", "reveal", "secret", "mystery", "solve"
}

def load_common_words() -> Set[str]:
    """
    Load common words from file or return a default set if file not found.
    
    Returns:
        Set[str]: A set of common words to exclude from character detection.
    """
    try:
        if os.path.exists(COMMON_WORDS_PATH):
            with open(COMMON_WORDS_PATH, 'r', encoding='utf-8') as f:
                return {w.lower().strip() for w in f.readlines() if w.strip()}
        else:
            logger.warning(f"Common words file not found at {COMMON_WORDS_PATH}")
            # Return a small default set
            return {"the", "a", "an", "and", "or", "but", "if", "then", "so", "as",
                   "at", "by", "for", "from", "in", "into", "of", "on", "to", "with"}
    except Exception as e:
        logger.error(f"Error loading common words: {str(e)}")
        return set()

def extract_potential_entities(text: str) -> Counter:
    """
    Extract potential named entities (characters/places) from text.
    
    Args:
        text (str): The book text to analyze.
        
    Returns:
        Counter: Dictionary with entity names and their frequency.
    """
    # Load common words
    common_words = load_common_words()
    
    # Find all capitalized words (potential proper nouns)
    words = re.findall(r'\b([A-Z][a-z]{1,15})\b', text)
    
    # Filter out common words even if capitalized
    filtered_words = [word for word in words if word.lower() not in common_words]
    
    # Count occurrences
    return Counter(filtered_words)

def find_main_characters(text: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Find the most frequently mentioned characters in the text.
    
    Args:
        text (str): The book text to analyze.
        top_n (int): Number of top characters to return.
        
    Returns:
        List[Dict[str, Any]]: List of character dictionaries with name and frequency.
    """
    entities = extract_potential_entities(text)
    
    # Get the most common entities
    main_characters = [
        {"name": name, "occurrences": count}
        for name, count in entities.most_common(top_n)
    ]
    
    return main_characters

def extract_context(text: str, keyword: str, window: int = 150) -> List[str]:
    """
    Extract text surrounding instances of a keyword.
    
    Args:
        text (str): The book text to analyze.
        keyword (str): The keyword to find.
        window (int): Number of characters to include before and after the keyword.
        
    Returns:
        List[str]: List of text passages containing the keyword with context.
    """
    passages = []
    pattern = re.compile(fr'\b{re.escape(keyword)}\b', re.IGNORECASE)
    
    for match in pattern.finditer(text):
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        passage = text[start:end]
        
        # Clean up the passage
        passage = re.sub(r'\s+', ' ', passage).strip()
        passages.append(passage)
        
    return passages

def generate_synopsis(text: str, main_characters: List[Dict[str, Any]], max_passages: int = 5) -> List[str]:
    """
    Generate a synopsis by finding passages containing interesting keywords.
    
    Args:
        text (str): The book text to analyze.
        main_characters (List[Dict[str, Any]]): List of main characters.
        max_passages (int): Maximum number of passages to include.
        
    Returns:
        List[str]: List of passages forming a rough synopsis.
    """
    all_passages = []
    character_names = [char["name"] for char in main_characters[:5]]
    
    # Find passages containing interesting keywords and main characters
    for keyword in INTERESTING_KEYWORDS:
        passages = extract_context(text, keyword)
        
        # Filter to include only passages that mention main characters
        for passage in passages:
            if any(char in passage for char in character_names):
                all_passages.append(passage)
    
    # Deduplicate and limit
    unique_passages = []
    seen = set()
    
    for passage in all_passages:
        # Create a signature by taking first 50 chars to avoid almost identical passages
        signature = passage[:50]
        if signature not in seen:
            seen.add(signature)
            unique_passages.append(passage)
            
            if len(unique_passages) >= max_passages:
                break
    
    return unique_passages

def find_easter_egg(text: str, main_characters: List[Dict[str, Any]]) -> Optional[str]:
    """
    Find a random interesting passage containing "first" and a main character.
    
    Args:
        text (str): The book text to analyze.
        main_characters (List[Dict[str, Any]]): List of main characters.
        
    Returns:
        Optional[str]: An interesting passage or None if none found.
    """
    character_names = [char["name"] for char in main_characters[:5]]
    first_passages = extract_context(text, "first")
    
    # Filter to include only passages that mention main characters
    valid_passages = [
        passage for passage in first_passages
        if any(char in passage for char in character_names)
    ]
    
    if valid_passages:
        return random.choice(valid_passages)
    return None

def analyze_book_text(text: str) -> Dict[str, Any]:
    """
    Analyze book text and extract key information.
    
    Args:
        text (str): The book text to analyze.
        
    Returns:
        Dict[str, Any]: Dictionary containing main characters, synopsis, and easter egg.
    """
    # Extract main characters
    main_characters = find_main_characters(text)
    
    # Generate synopsis
    synopsis = generate_synopsis(text, main_characters)
    
    # Find easter egg
    easter_egg = find_easter_egg(text, main_characters)
    
    return {
        "main_characters": [char["name"] for char in main_characters],
        "main_characters_details": main_characters,
        "synopsis": synopsis,
        "easter_egg": easter_egg if easter_egg else "No interesting first passage found."
    }

def analyze_dummy_book() -> Dict[str, Any]:
    """
    Generate a dummy book analysis for testing purposes.
    
    Returns:
        Dict[str, Any]: Dictionary containing mock main characters, synopsis, and easter egg.
    """
    return {
        "main_characters": ["Elizabeth", "Darcy", "Jane", "Bingley", "Wickham", "Lydia", "Collins"],
        "main_characters_details": [
            {"name": "Elizabeth", "occurrences": 635},
            {"name": "Darcy", "occurrences": 418},
            {"name": "Jane", "occurrences": 292},
            {"name": "Bingley", "occurrences": 257},
            {"name": "Wickham", "occurrences": 194},
            {"name": "Lydia", "occurrences": 176},
            {"name": "Collins", "occurrences": 165},
        ],
        "synopsis": [
            "Elizabeth felt herself growing more angry every moment; yet she tried to the utmost to speak with composure when she said: \"You are mistaken, Mr. Darcy, if you suppose that the mode of your declaration affected me in any other way, than as it spared me the concern which I might have felt in refusing you, had you behaved in a more gentlemanlike manner.\"",
            "\"From the very beginning—from the first moment, I may almost say—of my acquaintance with you, your manners, impressing me with the fullest belief of your arrogance, your conceit, and your selfish disdain of the feelings of others, were such as to form the groundwork of disapprobation on which succeeding events have built so immovable a dislike; and I had not known you a month before I felt that you were the last man in the world whom I could ever be prevailed on to marry.\"",
            "The tumult of her mind, was now painfully great. She knew not how to support herself, and from actual weakness sat down and cried for half-an-hour. Her astonishment, as she reflected on what had passed, was increased by every review of it.",
            "\"In vain I have struggled. It will not do. My feelings will not be repressed. You must allow me to tell you how ardently I admire and love you.\" Elizabeth's astonishment was beyond expression. She stared, coloured, doubted, and was silent.",
        ],
        "easter_egg": "Her father captivated by youth and beauty, and that appearance of good humour which youth and beauty generally give, had married a woman whose weak understanding and illiberal mind had very early in their marriage put an end to all real affection for her. Respect, esteem, and confidence had vanished for ever; and all his views of domestic happiness were overthrown. But Mr. Bennet was not of a disposition to seek comfort for the disappointment which his own imprudence had brought on."
    }
