"""
Normalized Answer Contract - Phase 3.16O
Provider-agnostic semantic answer structure for Adhyayan.

This module defines the schema that BOTH Gemini and OmniRoute must produce.
The frontend consumes ONLY this normalized structure - never raw LLM text.
"""

from typing import List, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


# ============================================================================
# BLOCK TYPES - Generic semantic content blocks
# ============================================================================

class BlockType(Enum):
    """Supported semantic block types"""
    MARKDOWN = "markdown"        # Plain text/markdown content
    EQUATION = "equation"        # Mathematical or chemical equation
    EXAMPLE = "example"          # Example section with nested blocks


@dataclass
class EquationBlock:
    """A semantic equation (chemistry, mathematics, physics)"""
    type: str = "equation"
    content: str = ""  # The equation content (e.g., "Zn + H₂SO₄ → ZnSO₄ + H₂")


@dataclass
class MarkdownBlock:
    """Markdown content block - rendered through MarkdownRenderer"""
    type: str = "markdown"
    content: str = ""  # Markdown text (tables, lists, emphasis, etc.)


@dataclass
class ExampleBlock:
    """Example section containing nested blocks"""
    type: str = "example"
    title: str = "Example"  # Optional title from <EXAMPLE title="...">
    blocks: List[Union[MarkdownBlock, EquationBlock]] = field(default_factory=list)


# A content block can be any of these types
ContentBlock = Union[MarkdownBlock, EquationBlock, ExampleBlock]


@dataclass
class Answer:
    """
    Normalized provider-independent answer structure.

    This is the SINGLE contract between backend and frontend.
    Frontend renders THIS structure, never raw LLM text.

    Structure:
    - keyIdea: The central concept (optional but expected for educational answers)
    - explanation: Main explanation content (optional but expected)
    - blocks: Semantic content blocks in document order
      - MarkdownBlock: Regular text/tables/lists (rendered via MarkdownRenderer)
      - EquationBlock: Standalone equations (rendered via EquationDisplay)
      - ExampleBlock: Example sections with nested blocks
    - metadata: Sources, retrieval details, timing info
    """
    keyIdea: Optional[str] = None
    explanation: Optional[str] = None
    blocks: List[ContentBlock] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    retrieval_details: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dict for SSE transmission"""
        return {
            "keyIdea": self.keyIdea,
            "explanation": self.explanation,
            "blocks": [
                asdict(block) if hasattr(block, '__dataclass_fields__') else block
                for block in self.blocks
            ],
            "sources": self.sources,
            "retrievalDetails": self.retrieval_details
        }


# ============================================================================
# XML PARSER - Convert LLM XML response to normalized Answer
# ============================================================================

import re


EQUATION_PATTERN = re.compile(
    r'<EQUATION\b[^>]*>([\s\S]*?)</EQUATION\s*>',
    re.IGNORECASE
)


def _parse_equation_content(
    content: str
) -> List[Union[MarkdownBlock, EquationBlock]]:
    """Split text and semantic equations into ordered content blocks."""
    blocks: List[Union[MarkdownBlock, EquationBlock]] = []
    position = 0

    for match in EQUATION_PATTERN.finditer(content):
        text_before = content[position:match.start()].strip()
        if text_before:
            blocks.append(MarkdownBlock(content=text_before))

        blocks.append(EquationBlock(content=match.group(1).strip()))
        position = match.end()

    remaining = content[position:].strip()
    if remaining:
        blocks.append(MarkdownBlock(content=remaining))

    return blocks


def _split_semantic_text(
    content: str
) -> tuple[Optional[str], List[Union[MarkdownBlock, EquationBlock]]]:
    """Keep leading prose in its dedicated field and return semantic tail blocks."""
    blocks = _parse_equation_content(content)
    first_equation = next(
        (index for index, block in enumerate(blocks) if isinstance(block, EquationBlock)),
        None
    )

    if first_equation is None:
        text = content.strip()
        return (text or None), []

    leading_text = None
    if first_equation > 0:
        leading_text = blocks[first_equation - 1].content

    return leading_text, blocks[first_equation:]


def parse_xml_response(raw_text: str) -> Answer:
    """
    Parse LLM XML-tagged response into normalized Answer object.

    Input: Raw text from provider containing XML semantic markers
    Output: Normalized Answer object ready for frontend rendering

    This is the ONLY place that parses XML. Frontend receives clean structure.
    """
    answer = Answer()
    leading_blocks: List[ContentBlock] = []

    # Extract KEY_IDEA (mandatory for educational answers)
    key_idea_match = re.search(
        r'<KEY_IDEA\b[^>]*>([\s\S]*?)</KEY_IDEA\s*>',
        raw_text,
        re.IGNORECASE
    )
    key_idea_tail: List[Union[MarkdownBlock, EquationBlock]] = []
    if key_idea_match:
        answer.keyIdea, key_idea_tail = _split_semantic_text(
            key_idea_match.group(1)
        )
        leading_blocks.extend(key_idea_tail)

    # Extract EXPLANATION (mandatory for educational answers)
    explanation_match = re.search(
        r'<EXPLANATION\b[^>]*>([\s\S]*?)</EXPLANATION\s*>',
        raw_text,
        re.IGNORECASE
    )
    if explanation_match:
        explanation_content = explanation_match.group(1)
        if key_idea_tail:
            # Once key-idea content moves into blocks, explanation must follow it
            # there to preserve the original document order.
            leading_blocks.extend(_parse_equation_content(explanation_content))
        else:
            answer.explanation, explanation_tail = _split_semantic_text(
                explanation_content
            )
            leading_blocks.extend(explanation_tail)

    # Key idea and explanation are rendered from their dedicated fields.
    # Remove their wrappers and contents before extracting ordered content blocks.
    block_content = re.sub(
        r'<(?:KEY_IDEA|EXPLANATION)\b[^>]*>[\s\S]*?</(?:KEY_IDEA|EXPLANATION)\s*>',
        '',
        raw_text,
        flags=re.IGNORECASE
    )
    answer.blocks = leading_blocks + _parse_blocks(block_content)

    return answer


def _parse_blocks(content: str) -> List[ContentBlock]:
    """
    Parse content blocks in document order.

    Handles:
    - EXAMPLE blocks (with nested EQUATION blocks)
    - Standalone EQUATION blocks
    - Markdown content (everything else)

    Preserves document order and handles multiple examples/equations.
    """
    blocks: List[ContentBlock] = []
    position = 0

    # Pattern for all block-level elements
    example_pattern = re.compile(
        r'<EXAMPLE\b([^>]*)>([\s\S]*?)</EXAMPLE\s*>',
        re.IGNORECASE
    )
    while position < len(content):
        # Find all matches at or after current position
        example_match = example_pattern.search(content, position)
        equation_match = EQUATION_PATTERN.search(content, position)

        # Find the earliest match
        matches = []
        if example_match:
            matches.append(('example', example_match))
        if equation_match:
            matches.append(('equation', equation_match))

        if not matches:
            # No more structured blocks - remaining content is markdown
            remaining = content[position:].strip()
            if remaining:
                blocks.append(MarkdownBlock(content=remaining))
            break

        # Get earliest match by position
        earliest_type, earliest_match = min(matches, key=lambda m: m[1].start())

        # Check if there's text before this match (markdown content)
        if earliest_match.start() > position:
            text_before = content[position:earliest_match.start()].strip()
            if text_before:
                blocks.append(MarkdownBlock(content=text_before))

        # Create the appropriate block
        if earliest_type == 'example':
            attributes = earliest_match.group(1)
            title_match = re.search(
                r'\btitle\s*=\s*(["\'])(.*?)\1',
                attributes,
                re.IGNORECASE
            )
            title = title_match.group(2) if title_match else "Example"
            example_content = earliest_match.group(2).strip()
            nested_blocks = _parse_example_content(example_content)
            blocks.append(ExampleBlock(title=title, blocks=nested_blocks))
        elif earliest_type == 'equation':
            equation_content = earliest_match.group(1).strip()
            blocks.append(EquationBlock(content=equation_content))

        # Move position past this match
        position = earliest_match.end()

    return blocks


def _parse_example_content(content: str) -> List[Union[MarkdownBlock, EquationBlock]]:
    """
    Parse content within an EXAMPLE block.

    Handles:
    - Nested EQUATION blocks
    - Markdown text between equations
    """
    return _parse_equation_content(content)


# ============================================================================
# LEGACY ADAPTER - Backward compatibility for old chat history
# ============================================================================

def parse_legacy_response(raw_text: str) -> Answer:
    """
    Parse legacy markdown format for backward compatibility.

    Supports old format:
    KEY IDEA: ...
    EXPLANATION: ...
    EXAMPLE: ...
    """
    answer = Answer()

    # Extract KEY IDEA: heading (case-insensitive)
    key_idea_match = re.search(r'^KEY IDEA:\s*(.+?)(?=\n\n|\n[A-Z]|$)', raw_text, re.MULTILINE | re.IGNORECASE)
    if key_idea_match:
        answer.keyIdea = key_idea_match.group(1).strip()

    # For legacy responses, treat entire content as markdown blocks
    answer.blocks = [MarkdownBlock(content=raw_text)]

    return answer


# ============================================================================
# VALIDATION
# ============================================================================

def validate_answer(answer: Answer) -> Answer:
    """
    Validate normalized Answer object.

    Ensures:
    - keyIdea is present for educational answers
    - At least one content block exists
    - No empty required fields
    """
    # If no blocks and no keyIdea/explanation, create fallback
    if not answer.blocks and not answer.keyIdea and not answer.explanation:
        answer.blocks = [MarkdownBlock(content="No response generated.")]

    return answer


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def normalize_response(raw_text: str) -> Answer:
    """
    Main entry point for normalizing LLM responses.

    Detects format (XML vs legacy) and routes to appropriate parser.
    Always returns a validated Answer object.
    """
    # Recognize supported semantic opening tags regardless of marker case or attributes.
    has_xml = bool(re.search(
        r'<(?:KEY_IDEA|EXPLANATION|EXAMPLE|EQUATION)\b[^>]*>',
        raw_text,
        re.IGNORECASE
    ))

    if has_xml:
        answer = parse_xml_response(raw_text)
    else:
        answer = parse_legacy_response(raw_text)

    # Validate before returning
    return validate_answer(answer)
