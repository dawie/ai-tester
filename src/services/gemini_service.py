"""
Simple Gemini Service for MVP

Sends page content to Gemini API to generate test cases.
"""

import os
import time
from google import genai
from typing import List
from ..models.test_case import TestCase, TestStatus
from ..models.page_capture import PageCapture
from ..lib.error_handling import ApiError, handle_api_error
from datetime import datetime


class GeminiService:
    """Simple service to generate test cases using Gemini API."""
    
    def __init__(self, rate_limit_delay: float = 2.0):
        """
        Initialize the Gemini service with API key from environment.
        
        Args:
            rate_limit_delay: Delay in seconds between API calls to avoid rate limits (default: 2.0)
        """
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ApiError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")
        
        # Configure Gemini
        self.client = genai.Client(api_key=api_key)
        self.rate_limit_delay = rate_limit_delay
        self.last_api_call_time = 0
        print(f"🤖 Gemini API configured successfully (rate limit delay: {rate_limit_delay}s)")
    
    def generate_test_cases(self, page_capture: PageCapture) -> List[TestCase]:
        """
        Generate test cases from page capture.
        
        Args:
            page_capture: Captured page content and metadata
            
        Returns:
            List of generated test cases
        """
        try:
            # Rate limiting: wait if needed
            self._apply_rate_limit()
            
            print(f"🧠 Generating test cases for: {page_capture.url}")
            
            # Create a focused prompt for test generation
            prompt = self._create_test_generation_prompt(page_capture)
            
            # Call Gemini API
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            
            if not response.text:
                raise ApiError("Gemini API returned empty response")
            
            # Parse the response and create test cases
            test_cases = self._parse_response_to_test_cases(response.text, page_capture)
            
            print(f"✅ Generated {len(test_cases)} test cases")
            return test_cases
            
        except Exception as e:
            handle_api_error(e, "test case generation")
    
    def _apply_rate_limit(self):
        """Apply rate limiting by waiting between API calls."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last_call
            print(f"⏱️  Rate limiting: waiting {wait_time:.1f}s before API call...")
            time.sleep(wait_time)
        
        self.last_api_call_time = time.time()
    
    def _create_test_generation_prompt(self, page_capture: PageCapture) -> str:
        """Create a focused prompt for test generation."""
        
        # Extract key elements from HTML for context
        html_snippet = self._extract_key_elements(page_capture.html_content)
        
        # Extract title from HTML content
        title = "Unknown Page"
        if "<title>" in page_capture.html_content:
            start = page_capture.html_content.find("<title>") + 7
            end = page_capture.html_content.find("</title>", start)
            if end > start:
                title = page_capture.html_content[start:end]
        
        prompt = f"""
You are an expert QA engineer creating Playwright tests in Python. 

Analyze this web page and generate practical test cases:

**Page Information:**
- URL: {page_capture.url}
- Title: {title}

**Key HTML Elements:**
{html_snippet}

**Requirements:**
1. Generate 2-3 focused test cases
2. Use pytest-playwright syntax
3. Include proper imports and setup
4. Focus on the most important user workflows
5. Use stable selectors (text content, roles, or data attributes when possible)
6. Each test should be a complete, runnable function

**Format your response as:**
TEST_CASE_1:
```python
# Test case code here
```

TEST_CASE_2:
```python
# Test case code here
```

Focus on realistic user scenarios like navigation, form submission, or content verification.
"""
        return prompt
    
    def _extract_key_elements(self, html_content: str) -> str:
        """Extract key interactive elements from HTML for prompt context."""
        
        # Simple extraction - in a full implementation we'd use BeautifulSoup
        # For MVP, just include a reasonable snippet
        
        # Take first 2000 characters and look for common patterns
        snippet = html_content[:2000]
        
        # Look for key elements (simplified)
        key_elements = []
        
        if '<button' in snippet.lower():
            key_elements.append("- Contains buttons for user interaction")
        if '<input' in snippet.lower():
            key_elements.append("- Contains form inputs")
        if '<a href' in snippet.lower():
            key_elements.append("- Contains navigation links")
        if '<form' in snippet.lower():
            key_elements.append("- Contains forms for data submission")
        if '<nav' in snippet.lower():
            key_elements.append("- Contains navigation menu")
        
        if not key_elements:
            key_elements.append("- Basic content page")
        
        return "\n".join(key_elements) + f"\n\nHTML Sample:\n{snippet}..."
    
    def _parse_response_to_test_cases(self, response_text: str, page_capture: PageCapture) -> List[TestCase]:
        """Parse Gemini response into TestCase objects."""
        
        test_cases = []
        
        # Extract title from HTML
        title = "page"
        if "<title>" in page_capture.html_content:
            start = page_capture.html_content.find("<title>") + 7
            end = page_capture.html_content.find("</title>", start)
            if end > start:
                title = page_capture.html_content[start:end].lower().replace(' ', '_')
        
        # Split response by TEST_CASE markers
        parts = response_text.split('TEST_CASE_')
        
        for i, part in enumerate(parts[1:], 1):  # Skip first part before TEST_CASE_1
            try:
                # Extract code between ```python and ```
                if '```python' in part and '```' in part:
                    start = part.find('```python') + 9
                    end = part.find('```', start)
                    if end > start:
                        test_code = part[start:end].strip()
                        
                        # Create test case
                        test_case = TestCase(
                            name=f"test_{title}_{i}",
                            description=f"Generated test case {i} for {page_capture.url}",
                            target_url=page_capture.url,
                            source_page_capture_id=page_capture.id,
                            test_code=test_code,
                            status=TestStatus.DRAFT,
                            generated_by="gemini-2.0-flash-exp"
                        )
                        
                        test_cases.append(test_case)
                        
            except Exception as e:
                print(f"⚠️ Could not parse test case {i}: {e}")
                continue
        
        if not test_cases:
            # Fallback: create a basic test case
            basic_test = self._create_fallback_test_case(page_capture)
            test_cases.append(basic_test)
        
        return test_cases
    
    def _create_fallback_test_case(self, page_capture: PageCapture) -> TestCase:
        """Create a basic fallback test case if parsing fails."""
        
        # Extract title from HTML
        title = "page"
        if "<title>" in page_capture.html_content:
            start = page_capture.html_content.find("<title>") + 7
            end = page_capture.html_content.find("</title>", start)
            if end > start:
                title = page_capture.html_content[start:end]
        
        test_code = f'''
import pytest
from playwright.sync_api import Page

def test_page_loads(page: Page):
    """Test that the page loads successfully."""
    page.goto("{page_capture.url}")
    assert page.title() == "{title}"
    assert page.is_visible("body")
'''
        
        return TestCase(
            name=f"test_{title.lower().replace(' ', '_')}_basic",
            description=f"Basic page load test for {title}",
            target_url=page_capture.url,
            source_page_capture_id=page_capture.id,
            test_code=test_code.strip(),
            status=TestStatus.DRAFT,
            generated_by="fallback"
        )