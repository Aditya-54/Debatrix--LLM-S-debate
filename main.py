from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import sys
import google.generativeai as genai
import os
from typing import Dict, Tuple

class DebateSystem:
    def __init__(self, api_key=None):
        """Initialize the Debate System with Gemini API."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided or set as GEMINI_API_KEY environment variable")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def set_model(self, model_name):
        """Set the model to use for generation."""
        self.model = genai.GenerativeModel(model_name)

    def get_pros(self, topic: str) -> str:
        """Generate pro arguments for a given topic."""
        prompt = f"""You are a professional debater arguing in favor of the topic: {topic}
        
        Requirements:
        1. Generate a strong, evidence-based argument
        2. Include specific examples and data
        3. Use web search to find relevant sources and citations
        4. Format the response with clear points and proper citations
        
        Generate a comprehensive argument with proper citations:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating pro arguments: {str(e)}"

    def get_cons(self, topic: str) -> str:
        """Generate con arguments for a given topic."""
        prompt = f"""You are a professional debater arguing against the topic: {topic}
        
        Requirements:
        1. Generate a strong, evidence-based counter-argument
        2. Include specific examples and data
        3. Use web search to find relevant sources and citations
        4. Format the response with clear points and proper citations
        
        Generate a comprehensive counter-argument with proper citations:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating con arguments: {str(e)}"

    def judge_debate(self, topic: str, pros: str, cons: str) -> str:
        """Generate a judgment for the debate."""
        prompt = f"""You are an expert debate judge evaluating the following debate:

Topic: {topic}

Pro Arguments:
{pros}

Con Arguments:
{cons}

Please provide a comprehensive judgment that includes:
1. Analysis of each side's strongest arguments
2. Evaluation of evidence and citations used
3. Assessment of argument structure and delivery
4. Final verdict with clear reasoning
5. Suggestions for improvement

Format your response clearly with these sections:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating judgment: {str(e)}"

    def run_full_debate(self, topic: str) -> Dict[str, str]:
        """Run a complete debate on a given topic."""
        try:
            pros = self.get_pros(topic)
            cons = self.get_cons(topic)
            judgment = self.judge_debate(topic, pros, cons)
            
            return {
                "topic": topic,
                "pros": pros,
                "cons": cons,
                "judgment": judgment
            }
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Initialize with your API key
    debate = DebateSystem(api_key="AIzaSyB_W9t18sgLbGXoD_zeqPaLkF8oyPPO19g")

    # debate = DebateSystem()
    
    # Choose a debate topic
    topic = "online gaming"
    
    result = debate.run_full_debate(topic)
    print(f"DEBATE TOPIC: {result['topic']}")
    print("\nPROS:")
    print(result['pros'])
    print("\nCONS:")
    print(result['cons'])
    print("\nJUDGMENT:")
    print(result['judgment'])


 