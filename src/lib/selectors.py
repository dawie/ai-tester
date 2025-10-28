"""
Selector Utilities

Generates stable selectors prioritizing text content, ARIA roles, and data-testid attributes.
"""

from typing import Dict, List, Tuple
from ..models.test_case import SelectorInfo


def generate_stable_selector(element_type: str, element_text: str = "", element_attributes: Dict[str, str] = None) -> SelectorInfo:
    """
    Generate stable selector for an element, prioritizing stable attributes.
    
    Args:
        element_type: Type of element (button, input, link, etc.)
        element_text: Visible text content of element
        element_attributes: Element attributes (id, class, data-testid, etc.)
        
    Returns:
        SelectorInfo with primary and fallback selectors
    """
    if element_attributes is None:
        element_attributes = {}
    
    selectors = []
    stability_scores = []
    
    # Priority 1: data-testid (most stable)
    if 'data-testid' in element_attributes:
        selectors.append(f"[data-testid='{element_attributes['data-testid']}']")
        stability_scores.append(0.9)
    
    # Priority 2: ARIA role + accessible name (very stable)
    if 'role' in element_attributes and element_text:
        role = element_attributes['role']
        selectors.append(f"role={role}[name='{element_text}']")
        stability_scores.append(0.85)
    
    # Priority 3: Text content (stable for static text)
    if element_text and element_type in ['button', 'link', 'span', 'div']:
        # Use getByText for exact text match
        selectors.append(f"text='{element_text}'")
        stability_scores.append(0.8)
    
    # Priority 4: ARIA label (fairly stable)
    if 'aria-label' in element_attributes:
        selectors.append(f"[aria-label='{element_attributes['aria-label']}']")
        stability_scores.append(0.75)
    
    # Priority 5: Placeholder text for inputs (fairly stable)
    if element_type == 'input' and 'placeholder' in element_attributes:
        selectors.append(f"[placeholder='{element_attributes['placeholder']}']")
        stability_scores.append(0.7)
    
    # Priority 6: ID (can be stable but often auto-generated)
    if 'id' in element_attributes and not element_attributes['id'].startswith(('auto-', 'generated-')):
        selectors.append(f"#{element_attributes['id']}")
        stability_scores.append(0.6)
    
    # Priority 7: Name attribute for form elements (moderately stable)
    if element_type in ['input', 'select', 'textarea'] and 'name' in element_attributes:
        selectors.append(f"[name='{element_attributes['name']}']")
        stability_scores.append(0.55)
    
    # Priority 8: Class names (less stable, depends on CSS framework)
    if 'class' in element_attributes:
        classes = element_attributes['class'].split()
        # Prefer semantic classes over utility classes
        semantic_classes = [c for c in classes if not any(
            util in c.lower() for util in ['btn-', 'text-', 'bg-', 'w-', 'h-', 'p-', 'm-', 'flex-']
        )]
        if semantic_classes:
            selectors.append(f".{semantic_classes[0]}")
            stability_scores.append(0.4)
    
    # Priority 9: Tag + type for form elements (least stable but better than nothing)
    if element_type in ['input', 'button'] and 'type' in element_attributes:
        selectors.append(f"{element_type}[type='{element_attributes['type']}']")
        stability_scores.append(0.3)
    
    # Priority 10: Tag selector only (very unstable)
    if not selectors:
        selectors.append(element_type)
        stability_scores.append(0.1)
    
    # Primary selector is the most stable one
    primary_selector = selectors[0] if selectors else element_type
    primary_score = stability_scores[0] if stability_scores else 0.1
    fallback_selectors = selectors[1:] if len(selectors) > 1 else []
    
    # Determine selector type
    selector_type = _determine_selector_type(primary_selector)
    
    return SelectorInfo(
        element_type=element_type,
        selector_text=primary_selector,
        selector_type=selector_type,
        stability_score=primary_score,
        fallback_selectors=fallback_selectors
    )


def _determine_selector_type(selector: str) -> str:
    """
    Determine the type of a selector.
    
    Args:
        selector: CSS selector string
        
    Returns:
        Selector type (css, text, role, data-testid)
    """
    if selector.startswith('data-testid=') or '[data-testid=' in selector:
        return 'data-testid'
    elif selector.startswith('role='):
        return 'role'
    elif selector.startswith('text='):
        return 'text'
    elif selector.startswith('[aria-label='):
        return 'aria-label'
    elif selector.startswith('#'):
        return 'id'
    elif selector.startswith('.'):
        return 'class'
    elif selector.startswith('['):
        return 'attribute'
    else:
        return 'css'


def generate_wait_strategy(element_type: str, selector_info: SelectorInfo) -> Tuple[str, int]:
    """
    Generate appropriate wait strategy for element interaction.
    
    Args:
        element_type: Type of element
        selector_info: Selector information
        
    Returns:
        Tuple of (wait_type, timeout_ms)
    """
    # Different wait strategies based on element type
    if element_type in ['button', 'link']:
        # Clickable elements should be visible and enabled
        return ('wait_for_selector_enabled', 5000)
    elif element_type in ['input', 'textarea', 'select']:
        # Form elements should be visible and not readonly
        return ('wait_for_selector_editable', 5000)
    elif element_type in ['div', 'span', 'p']:
        # Content elements just need to be visible
        return ('wait_for_selector_visible', 3000)
    else:
        # Default strategy
        return ('wait_for_selector_visible', 5000)


def generate_playwright_selector_code(selector_info: SelectorInfo, wait_strategy: Tuple[str, int] = None) -> str:
    """
    Generate Playwright Python code for selecting an element.
    
    Args:
        selector_info: Selector information
        wait_strategy: Optional wait strategy (wait_type, timeout)
        
    Returns:
        Python code string for Playwright selector
    """
    selector = selector_info.selector_text
    selector_type = selector_info.selector_type
    
    # Generate appropriate Playwright locator based on selector type
    if selector_type == 'text':
        # Remove 'text=' prefix for getByText
        text = selector.replace('text=', '').strip("'\"")
        locator_code = f"page.get_by_text('{text}')"
    elif selector_type == 'role':
        # Parse role selector: role=button[name='Click me']
        if '[name=' in selector:
            role = selector.split('=')[1].split('[')[0]
            name = selector.split("name='")[1].split("'")[0]
            locator_code = f"page.get_by_role('{role}', name='{name}')"
        else:
            role = selector.split('=')[1]
            locator_code = f"page.get_by_role('{role}')"
    elif selector_type == 'data-testid':
        # Extract data-testid value
        testid = selector.split("data-testid='")[1].split("'")[0]
        locator_code = f"page.get_by_test_id('{testid}')"
    elif selector_type == 'aria-label':
        # Extract aria-label value
        label = selector.split("aria-label='")[1].split("'")[0]
        locator_code = f"page.get_by_label('{label}')"
    else:
        # CSS selector fallback
        locator_code = f"page.locator('{selector}')"
    
    # Add wait strategy if specified
    if wait_strategy:
        wait_type, timeout = wait_strategy
        if wait_type == 'wait_for_selector_enabled':
            return f"{locator_code}.wait_for(state='visible', timeout={timeout})\n    element = {locator_code}"
        elif wait_type == 'wait_for_selector_editable':
            return f"{locator_code}.wait_for(state='editable', timeout={timeout})\n    element = {locator_code}"
        else:  # wait_for_selector_visible
            return f"{locator_code}.wait_for(state='visible', timeout={timeout})\n    element = {locator_code}"
    
    return f"element = {locator_code}"


def extract_selectors_from_html(html_content: str, element_types: List[str] = None) -> List[SelectorInfo]:
    """
    Extract potential selectors from HTML content for common interactive elements.
    
    Args:
        html_content: HTML content to analyze
        element_types: List of element types to extract (defaults to common interactive elements)
        
    Returns:
        List of SelectorInfo objects for found elements
    """
    if element_types is None:
        element_types = ['button', 'input', 'a', 'select', 'textarea']
    
    # This is a simplified implementation
    # In a real implementation, you'd use BeautifulSoup or similar to parse HTML
    selectors = []
    
    # For now, return empty list - this would be implemented with proper HTML parsing
    # when we have a real HTML parser dependency
    
    return selectors


def optimize_selectors_for_dynamic_content(selectors: List[SelectorInfo]) -> List[SelectorInfo]:
    """
    Optimize selectors to handle dynamic content better.
    
    Args:
        selectors: List of selectors to optimize
        
    Returns:
        Optimized list of selectors
    """
    optimized = []
    
    for selector in selectors:
        # Create optimized version that avoids dynamic attributes
        optimized_selector = SelectorInfo(
            element_type=selector.element_type,
            selector_text=selector.selector_text,
            selector_type=selector.selector_type,
            stability_score=selector.stability_score,
            fallback_selectors=selector.fallback_selectors
        )
        
        # Filter out potentially dynamic selectors from fallbacks
        filtered_fallbacks = []
        for fallback in selector.fallback_selectors:
            # Skip selectors that look auto-generated or contain timestamps
            if not any(pattern in fallback.lower() for pattern in ['auto-', 'generated-', 'timestamp', 'uuid']):
                filtered_fallbacks.append(fallback)
        
        optimized_selector.fallback_selectors = filtered_fallbacks
        optimized.append(optimized_selector)
    
    return optimized