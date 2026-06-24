"""
Scoring Module
==============
Handles quiz scoring, result calculation, and performance analysis.
"""

from typing import Dict, List, Optional, Tuple


class QuizScorer:
    """
    Handles scoring and result calculation for quizzes.
    """
    
    def __init__(self):
        """Initialize the quiz scorer."""
        self.reset()
    
    def reset(self):
        """Reset all scoring data."""
        self.user_answers = {}  # question_index -> selected_answer
        self.total_questions = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.score = 0
        self.percentage = 0.0
    
    def record_answer(self, question_index: int, selected_answer: str):
        """
        Record a user's answer for a question.
        
        Args:
            question_index: Index of the question
            selected_answer: The answer selected by the user (A, B, C, or D)
        """
        self.user_answers[question_index] = selected_answer
    
    def calculate_results(self, questions: List[Dict]) -> Dict:
        """
        Calculate the final results of the quiz.
        
        Args:
            questions: List of question dictionaries with correct_answer field
            
        Returns:
            Dictionary containing:
                - total_questions: Total number of questions
                - correct_count: Number of correct answers
                - wrong_count: Number of wrong answers
                - unanswered: Number of unanswered questions
                - score: Raw score (correct count)
                - percentage: Percentage score (0-100)
                - accuracy: Accuracy percentage
                - performance_message: Performance level message
                - results: List of per-question results
        """
        self.total_questions = len(questions)
        self.correct_count = 0
        self.wrong_count = 0
        
        results = []
        
        for idx, question in enumerate(questions):
            user_answer = self.user_answers.get(idx, None)
            correct_answer = question.get("correct_answer", "")
            
            is_correct = user_answer == correct_answer if user_answer else False
            
            if user_answer is None:
                pass  # Unanswered
            elif is_correct:
                self.correct_count += 1
            else:
                self.wrong_count += 1
            
            results.append({
                "question_index": idx,
                "question": question.get("question", ""),
                "options": question.get("options", []),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", ""),
                "was_answered": user_answer is not None
            })
        
        self.score = self.correct_count
        self.percentage = (self.correct_count / self.total_questions * 100) if self.total_questions > 0 else 0
        
        unanswered = sum(1 for r in results if not r["was_answered"])
        
        return {
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "wrong_count": self.wrong_count,
            "unanswered": unanswered,
            "score": self.score,
            "percentage": round(self.percentage, 1),
            "accuracy": round(self.percentage, 1),
            "performance_message": self.get_performance_message(self.percentage),
            "results": results
        }
    
    def get_performance_message(self, percentage: float) -> Dict:
        """
        Get a performance message based on the score percentage.
        
        Args:
            percentage: Score percentage (0-100)
            
        Returns:
            Dictionary with title, message, and emoji
        """
        if percentage >= 90:
            return {
                "title": "Outstanding Performance! 🏆",
                "message": "Exceptional! You have mastered this material with near-perfect accuracy. Your understanding is comprehensive and thorough.",
                "emoji": "🏆",
                "level": "outstanding"
            }
        elif percentage >= 75:
            return {
                "title": "Excellent Work! 🌟",
                "message": "Great job! You have a strong grasp of the material. Keep up the excellent work!",
                "emoji": "🌟",
                "level": "excellent"
            }
        elif percentage >= 50:
            return {
                "title": "Good Effort! 💪",
                "message": "You're on the right track! Review the areas where you made mistakes to strengthen your understanding.",
                "emoji": "💪",
                "level": "good"
            }
        else:
            return {
                "title": "Needs Improvement 📚",
                "message": "Don't give up! Review the material again and try the quiz once more. Practice makes perfect!",
                "emoji": "📚",
                "level": "needs_improvement"
            }
    
    def get_topic_performance(self, results: List[Dict], questions: List[Dict]) -> Dict:
        """
        Analyze performance by topic/category.
        Note: This is a simplified analysis since we don't have explicit topic tags.
        
        Args:
            results: List of per-question results
            questions: List of question dictionaries
            
        Returns:
            Dictionary with topic performance analysis
        """
        # Simple analysis - group by question length/complexity as a proxy
        simple_questions = []
        medium_questions = []
        complex_questions = []
        
        for idx, q in enumerate(questions):
            q_len = len(q.get("question", ""))
            if q_len < 60:
                simple_questions.append(idx)
            elif q_len < 120:
                medium_questions.append(idx)
            else:
                complex_questions.append(idx)
        
        def calc_group_accuracy(indices):
            if not indices:
                return 0
            correct = sum(1 for i in indices if i < len(results) and results[i]["is_correct"])
            return round(correct / len(indices) * 100, 1)
        
        return {
            "simple_accuracy": calc_group_accuracy(simple_questions),
            "medium_accuracy": calc_group_accuracy(medium_questions),
            "complex_accuracy": calc_group_accuracy(complex_questions),
            "simple_count": len(simple_questions),
            "medium_count": len(medium_questions),
            "complex_count": len(complex_questions)
        }
    
    def get_answer_summary(self, results: List[Dict]) -> Dict:
        """
        Get a summary of answer distribution.
        
        Args:
            results: List of per-question results
            
        Returns:
            Dictionary with answer distribution stats
        """
        answer_distribution = {"A": 0, "B": 0, "C": 0, "D": 0}
        correct_distribution = {"A": 0, "B": 0, "C": 0, "D": 0}
        
        for r in results:
            if r["was_answered"] and r["user_answer"] in answer_distribution:
                answer_distribution[r["user_answer"]] += 1
            if r["correct_answer"] in correct_distribution:
                correct_distribution[r["correct_answer"]] += 1
        
        return {
            "answer_distribution": answer_distribution,
            "correct_distribution": correct_distribution
        }