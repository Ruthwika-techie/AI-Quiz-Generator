"""
Quiz Generator Module
=====================
Generates multiple-choice questions from extracted PPT content.
Supports both real LLM (OpenAI/DeepSeek compatible) and intelligent mock generation.
"""

import json
import random
import re
from typing import Dict, List, Optional, Any

# Try to import OpenAI, but don't fail if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class QuizGeneratorError(Exception):
    """Custom exception for quiz generation errors."""
    pass


class QuizGenerator:
    """
    Main quiz generator class that creates MCQs from slide content.
    Supports real LLM API calls and intelligent fallback mock generation.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the quiz generator.
        
        Args:
            api_key: API key for LLM provider (OpenAI or DeepSeek compatible)
            api_url: Custom API endpoint URL (for DeepSeek or other providers)
            model: Model name to use
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.client = None
        
        if api_key and OPENAI_AVAILABLE:
            client_kwargs = {"api_key": api_key}
            if api_url:
                client_kwargs["base_url"] = api_url
            self.client = OpenAI(**client_kwargs)
    
    def generate_quiz(
        self,
        slide_content: Dict,
        num_questions: int = 10,
        difficulty: str = "Medium",
        use_llm: bool = True
    ) -> List[Dict]:
        """
        Generate quiz questions from slide content.
        
        Args:
            slide_content: Dictionary from ppt_parser.extract_ppt_content()
            num_questions: Number of questions to generate (5-30)
            difficulty: Difficulty level - "Simple", "Medium", or "Complex"
            use_llm: Whether to use LLM API (True) or mock generation (False)
            
        Returns:
            List of question dictionaries
        """
        all_text = slide_content.get("all_text", "")
        
        if not all_text.strip():
            raise QuizGeneratorError("No text content found in the PowerPoint file.")
        
        # Validate and clamp question count
        num_questions = max(5, min(30, num_questions))
        
        # Try LLM generation first if available and requested
        if use_llm and self.client and OPENAI_AVAILABLE:
            try:
                return self._generate_with_llm(all_text, num_questions, difficulty)
            except Exception as e:
                # Fall back to mock generation if LLM fails
                print(f"LLM generation failed: {e}. Falling back to mock generation.")
                return self._generate_mock_quiz(all_text, num_questions, difficulty)
        else:
            return self._generate_mock_quiz(all_text, num_questions, difficulty)
    
    def _generate_with_llm(self, text: str, num_questions: int, difficulty: str) -> List[Dict]:
        """
        Generate questions using LLM API.
        
        Args:
            text: Extracted text from slides
            num_questions: Number of questions to generate
            difficulty: Difficulty level
            
        Returns:
            List of question dictionaries
        """
        difficulty_instructions = {
            "Simple": "Create simple, direct factual questions that test basic recall of the content.",
            "Medium": "Create conceptual questions that test understanding and comprehension of the material.",
            "Complex": "Create analytical questions that require application, analysis, and critical thinking about the content."
        }
        
        prompt = f"""You are an expert quiz generator. Based on the following content from a PowerPoint presentation, generate {num_questions} multiple-choice questions.

Content:
{text[:8000]}

Difficulty: {difficulty}
{difficulty_instructions.get(difficulty, difficulty_instructions["Medium"])}

IMPORTANT RULES:
1. Each question must have exactly 4 options (A, B, C, D)
2. Exactly one correct answer per question
3. Provide a clear explanation for the correct answer
4. Questions must be based on the content provided
5. Distractors should be plausible but incorrect
6. Vary the position of the correct answer (don't always make it 'A')

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
[
  {{
    "question": "What is...?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "B",
    "explanation": "Explanation of why B is correct."
  }}
]"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert quiz generator. Always return valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up response - remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        try:
            questions = json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON array in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    questions = json.loads(json_match.group())
                except json.JSONDecodeError:
                    raise QuizGeneratorError("Failed to parse LLM response as JSON.")
            else:
                raise QuizGeneratorError("Failed to parse LLM response as JSON.")
        
        # Validate and fix questions
        validated_questions = []
        for q in questions:
            if self._validate_question(q):
                validated_questions.append(q)
        
        if not validated_questions:
            raise QuizGeneratorError("No valid questions generated.")
        
        return validated_questions[:num_questions]
    
    def _generate_mock_quiz(self, text: str, num_questions: int, difficulty: str) -> List[Dict]:
        """
        Generate questions intelligently from slide text without an LLM.
        Uses NLP-like techniques to extract key information and create questions.
        
        Args:
            text: Extracted text from slides
            num_questions: Number of questions to generate
            difficulty: Difficulty level
            
        Returns:
            List of question dictionaries
        """
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        # Filter meaningful sentences (not too short, not too long)
        meaningful_sentences = [
            s for s in sentences 
            if 15 < len(s) < 300 and not s.startswith(('http', 'www', '©', '•', '●'))
        ]
        
        if len(meaningful_sentences) < num_questions:
            # If not enough sentences, use all text chunks
            chunks = self._chunk_text(text, num_questions)
            meaningful_sentences = chunks
        
        # Shuffle to get variety
        random.shuffle(meaningful_sentences)
        
        # Select sentences based on difficulty
        if difficulty == "Simple":
            # Use shorter, more direct sentences
            selected = [s for s in meaningful_sentences if len(s) < 100][:num_questions]
        elif difficulty == "Complex":
            # Use longer, more complex sentences
            selected = [s for s in meaningful_sentences if len(s) > 80][:num_questions]
        else:
            selected = meaningful_sentences[:num_questions]
        
        # Ensure we have enough
        if len(selected) < num_questions:
            selected = meaningful_sentences[:num_questions]
        
        # Generate questions from selected sentences
        questions = []
        for sentence in selected:
            q = self._create_question_from_sentence(sentence, difficulty)
            if q:
                questions.append(q)
        
        # If we still don't have enough, create fill-in questions
        while len(questions) < num_questions:
            q = self._create_fallback_question(text)
            if q:
                questions.append(q)
        
        return questions[:num_questions]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences intelligently."""
        # Split on sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Clean up
        sentences = [s.strip() for s in sentences if s.strip()]
        # Remove bullet points and list markers
        sentences = [re.sub(r'^[\d•●\-–—*+]+\.?\s*', '', s) for s in sentences]
        return [s for s in sentences if len(s) > 10]
    
    def _chunk_text(self, text: str, num_chunks: int) -> List[str]:
        """Split text into roughly equal chunks."""
        words = text.split()
        if not words:
            return []
        
        chunk_size = max(1, len(words) // num_chunks)
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _create_question_from_sentence(self, sentence: str, difficulty: str) -> Optional[Dict]:
        """
        Create a multiple-choice question from a single sentence.
        Uses intelligent text manipulation to create meaningful questions.
        """
        # Clean the sentence
        sentence = sentence.strip()
        if len(sentence) < 20:
            return None
        
        # Extract key terms (capitalized words, numbers, important terms)
        words = sentence.split()
        key_terms = [w for w in words if w[0].isupper() and len(w) > 2] if words else []
        numbers = re.findall(r'\d+', sentence)
        
        # Try to create a "what" question from the sentence
        question_templates = [
            self._create_what_question,
            self._create_which_question,
            self._create_definition_question,
            self._create_true_false_style,
        ]
        
        # Shuffle templates for variety
        random.shuffle(question_templates)
        
        for template in question_templates:
            result = template(sentence, key_terms, numbers, difficulty)
            if result:
                return result
        
        return None
    
    def _create_what_question(self, sentence: str, key_terms: List[str], numbers: List[str], difficulty: str) -> Optional[Dict]:
        """Create a 'What' type question."""
        # Find the main subject (first few words)
        words = sentence.split()
        if len(words) < 4:
            return None
        
        # Extract a key phrase to ask about
        if key_terms:
            subject = key_terms[0]
        else:
            subject = ' '.join(words[:min(3, len(words))])
        
        # Create question
        question = f"What is described by: '{sentence[:100]}...'?" if len(sentence) > 100 else f"What does the following describe: '{sentence}'?"
        
        # Create options
        correct = sentence[:80] + "..." if len(sentence) > 80 else sentence
        
        # Generate distractors from the text
        distractors = self._generate_distractors(sentence, key_terms, 3)
        
        if len(distractors) < 3:
            return None
        
        options = [correct] + distractors
        random.shuffle(options)
        
        correct_index = options.index(correct)
        correct_letter = chr(65 + correct_index)  # A, B, C, D
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_letter,
            "explanation": f"The correct answer is based on the content: {sentence}"
        }
    
    def _create_which_question(self, sentence: str, key_terms: List[str], numbers: List[str], difficulty: str) -> Optional[Dict]:
        """Create a 'Which' type question."""
        if not key_terms:
            return None
        
        subject = key_terms[0]
        
        # Create a question about the key term
        question = f"Which of the following best describes '{subject}'?"
        
        # The correct answer is the sentence context around the key term
        context_match = re.search(rf'.{{0,100}}{re.escape(subject)}.{{0,100}}', sentence)
        correct = context_match.group() if context_match else sentence[:100]
        
        distractors = self._generate_distractors(sentence, key_terms, 3)
        
        if len(distractors) < 3:
            return None
        
        options = [correct] + distractors
        random.shuffle(options)
        
        correct_index = options.index(correct)
        correct_letter = chr(65 + correct_index)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_letter,
            "explanation": f"'{subject}' is correctly described in the presentation content."
        }
    
    def _create_definition_question(self, sentence: str, key_terms: List[str], numbers: List[str], difficulty: str) -> Optional[Dict]:
        """Create a definition-style question."""
        # Look for definition patterns
        definition_patterns = [
            r'is\s+a\s+',
            r'is\s+an?\s+',
            r'refers\s+to\s+',
            r'means\s+',
            r'defined\s+as\s+',
            r'known\s+as\s+',
        ]
        
        for pattern in definition_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                # Split at the definition marker
                parts = re.split(pattern, sentence, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) == 2:
                    term = parts[0].strip()
                    definition = parts[1].strip()
                    
                    # Clean up
                    term = re.sub(r'^[A-Z][a-z]+', '', term).strip() if not term[0].isupper() else term
                    
                    if len(term) > 3 and len(definition) > 5:
                        question = f"What is '{term}'?"
                        correct = definition[:80] + "..." if len(definition) > 80 else definition
                        
                        distractors = self._generate_distractors(sentence, key_terms, 3)
                        if len(distractors) < 3:
                            continue
                        
                        options = [correct] + distractors
                        random.shuffle(options)
                        
                        correct_index = options.index(correct)
                        correct_letter = chr(65 + correct_index)
                        
                        return {
                            "question": question,
                            "options": options,
                            "correct_answer": correct_letter,
                            "explanation": f"'{term}' is defined as: {definition}"
                        }
        
        return None
    
    def _create_true_false_style(self, sentence: str, key_terms: List[str], numbers: List[str], difficulty: str) -> Optional[Dict]:
        """Create a question that asks about a specific detail."""
        words = sentence.split()
        if len(words) < 5:
            return None
        
        # Pick a random word/phrase to replace or ask about
        if numbers:
            # Ask about a number
            number = random.choice(numbers)
            question = f"According to the presentation, what number is associated with this content?"
            
            correct = number
            # Generate wrong numbers
            wrong_numbers = []
            for _ in range(3):
                wrong = str(int(number) + random.randint(-10, 10))
                if wrong != number and wrong not in wrong_numbers:
                    wrong_numbers.append(wrong)
            
            if len(wrong_numbers) < 3:
                return None
            
            options = [correct] + wrong_numbers
            random.shuffle(options)
            
            correct_index = options.index(correct)
            correct_letter = chr(65 + correct_index)
            
            return {
                "question": question,
                "options": options,
                "correct_answer": correct_letter,
                "explanation": f"The presentation states: {sentence}"
            }
        
        elif key_terms:
            # Ask about a key term
            term = random.choice(key_terms)
            question = f"Which statement about '{term}' is correct according to the presentation?"
            
            correct = sentence[:80] + "..." if len(sentence) > 80 else sentence
            distractors = self._generate_distractors(sentence, key_terms, 3)
            
            if len(distractors) < 3:
                return None
            
            options = [correct] + distractors
            random.shuffle(options)
            
            correct_index = options.index(correct)
            correct_letter = chr(65 + correct_index)
            
            return {
                "question": question,
                "options": options,
                "correct_answer": correct_letter,
                "explanation": f"Based on the content: {sentence}"
            }
        
        return None
    
    def _generate_distractors(self, sentence: str, key_terms: List[str], count: int) -> List[str]:
        """
        Generate plausible but incorrect distractor options.
        """
        distractors = []
        
        # Generic plausible-sounding wrong answers
        generic_wrong = [
            "This is not mentioned in the presentation.",
            "The presentation does not support this claim.",
            "This contradicts the presentation content.",
            "This is an incorrect interpretation of the material.",
            "The presentation suggests the opposite of this statement.",
            "This concept is not related to the topic discussed.",
            "This statement contains factual errors.",
            "The presentation explicitly rejects this idea.",
        ]
        
        # Use key terms to create topic-specific distractors
        if key_terms:
            for term in key_terms[1:]:  # Skip the first term (used as subject)
                if len(distractors) < count:
                    distractors.append(f"'{term}' is the key concept, but this is not what the question asks about.")
        
        # Fill remaining with generic distractors
        random.shuffle(generic_wrong)
        for d in generic_wrong:
            if len(distractors) < count:
                distractors.append(d)
        
        return distractors[:count]
    
    def _create_fallback_question(self, text: str) -> Optional[Dict]:
        """Create a fallback question when other methods fail."""
        words = text.split()
        if len(words) < 10:
            return None
        
        # Pick a random chunk of text
        start = random.randint(0, max(0, len(words) - 20))
        chunk = ' '.join(words[start:start + 15])
        
        if len(chunk) < 20:
            return None
        
        question = f"Based on the presentation content, which statement is correct?"
        correct = chunk[:80] + "..." if len(chunk) > 80 else chunk
        
        distractors = [
            "This concept is not discussed in the presentation.",
            "The presentation presents a different view on this topic.",
            "This statement misrepresents the presentation content.",
        ]
        
        options = [correct] + distractors
        random.shuffle(options)
        
        correct_index = options.index(correct)
        correct_letter = chr(65 + correct_index)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_letter,
            "explanation": f"This is directly supported by the presentation content."
        }
    
    def _validate_question(self, q: Dict) -> bool:
        """Validate that a question dictionary has all required fields."""
        required_keys = {"question", "options", "correct_answer", "explanation"}
        
        if not all(key in q for key in required_keys):
            return False
        
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            return False
        
        if q["correct_answer"] not in ("A", "B", "C", "D"):
            return False
        
        if not q["question"] or not q["explanation"]:
            return False
        
        return True
    
    def save_quiz_to_json(self, questions: List[Dict], file_path: str):
        """
        Save generated quiz questions to a JSON file.
        
        Args:
            questions: List of question dictionaries
            file_path: Path to save the JSON file
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
    
    def load_quiz_from_json(self, file_path: str) -> List[Dict]:
        """
        Load quiz questions from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of question dictionaries
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)