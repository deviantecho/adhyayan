import unittest

from scripts.answer_schema import (
    EquationBlock,
    ExampleBlock,
    MarkdownBlock,
    normalize_response,
)


class AnswerSchemaNormalizationTests(unittest.TestCase):
    def test_uppercase_semantic_xml_is_normalized(self):
        raw = """<KEY_IDEA>
A concept.
</KEY_IDEA>

<EXPLANATION>
An explanation.
</EXPLANATION>

<EXAMPLE title="Example">
Some explanation.

<EQUATION>
A + B -> C
</EQUATION>

More explanation.
</EXAMPLE>"""

        answer = normalize_response(raw)

        self.assertEqual(answer.keyIdea, "A concept.")
        self.assertEqual(answer.explanation, "An explanation.")
        self.assertEqual(len(answer.blocks), 1)
        example = answer.blocks[0]
        self.assertIsInstance(example, ExampleBlock)
        self.assertEqual(example.title, "Example")
        self.assertEqual(
            [type(block) for block in example.blocks],
            [MarkdownBlock, EquationBlock, MarkdownBlock],
        )
        self.assertNotIn("<KEY_IDEA>", example.blocks[0].content)

    def test_lowercase_semantic_xml_is_normalized(self):
        raw = """<key_idea>A concept.</key_idea>
<explanation>An explanation.</explanation>
<example title="Example">
Before.
<equation>x + y = z</equation>
After.
</example>"""

        answer = normalize_response(raw)

        self.assertEqual(answer.keyIdea, "A concept.")
        self.assertEqual(answer.explanation, "An explanation.")
        self.assertEqual(len(answer.blocks), 1)
        example = answer.blocks[0]
        self.assertIsInstance(example, ExampleBlock)
        self.assertTrue(any(isinstance(block, EquationBlock) for block in example.blocks))

    def test_example_with_title_attribute_is_detected(self):
        answer = normalize_response(
            '<EXAMPLE title="Any Example">Example content.</EXAMPLE>'
        )

        self.assertEqual(len(answer.blocks), 1)
        self.assertIsInstance(answer.blocks[0], ExampleBlock)
        self.assertEqual(answer.blocks[0].title, "Any Example")

    def test_legacy_markdown_remains_compatible(self):
        raw = """**KEY IDEA:**
A legacy concept.

**EXPLANATION:**
A legacy explanation."""

        answer = normalize_response(raw)

        self.assertIsNone(answer.keyIdea)
        self.assertIsNone(answer.explanation)
        self.assertEqual(len(answer.blocks), 1)
        self.assertIsInstance(answer.blocks[0], MarkdownBlock)
        self.assertEqual(answer.blocks[0].content, raw)

    def test_example_preserves_multiple_equations(self):
        raw = """<EXAMPLE title="Multiple steps">
Start.
<EQUATION>a = b</EQUATION>
Middle.
<EQUATION>b = c</EQUATION>
End.
</EXAMPLE>"""

        answer = normalize_response(raw)
        example = answer.blocks[0]

        self.assertIsInstance(example, ExampleBlock)
        equations = [
            block for block in example.blocks if isinstance(block, EquationBlock)
        ]
        self.assertEqual([block.content for block in equations], ["a = b", "b = c"])

    def test_equation_inside_explanation_becomes_ordered_block(self):
        raw = """<KEY_IDEA>A relationship.</KEY_IDEA>
<EXPLANATION>
For any two positive integers:

<EQUATION>
HCF(a, b) × LCM(a, b) = a × b
</EQUATION>

This identity links the two values.
</EXPLANATION>
<EXAMPLE title="Worked example">
Apply the identity.
<EQUATION>LCM(96, 404) = (96 × 404) / HCF(96, 404)</EQUATION>
</EXAMPLE>"""

        answer = normalize_response(raw)

        self.assertEqual(answer.explanation, "For any two positive integers:")
        self.assertEqual(
            [type(block) for block in answer.blocks],
            [EquationBlock, MarkdownBlock, ExampleBlock],
        )
        self.assertEqual(
            answer.blocks[0].content,
            "HCF(a, b) × LCM(a, b) = a × b",
        )
        self.assertEqual(answer.blocks[1].content, "This identity links the two values.")
        self.assertEqual(
            [type(block) for block in answer.blocks[2].blocks],
            [MarkdownBlock, EquationBlock],
        )
        rendered_text = "\n".join(
            [answer.explanation or ""]
            + [
                block.content
                for block in answer.blocks
                if isinstance(block, (MarkdownBlock, EquationBlock))
            ]
        )
        self.assertNotIn("<EQUATION", rendered_text.upper())
        self.assertEqual(
            rendered_text.count("HCF(a, b) × LCM(a, b) = a × b"),
            1,
        )

    def test_multiple_explanation_equations_preserve_order(self):
        raw = """<EXPLANATION>
Start with the first identity.
<EQUATION>a = b</EQUATION>
Then use the second identity.
<equation>b = c</equation>
Finish the explanation.
</EXPLANATION>
<EQUATION>c = d</EQUATION>"""

        answer = normalize_response(raw)

        self.assertEqual(answer.explanation, "Start with the first identity.")
        self.assertEqual(
            [type(block) for block in answer.blocks],
            [
                EquationBlock,
                MarkdownBlock,
                EquationBlock,
                MarkdownBlock,
                EquationBlock,
            ],
        )
        self.assertEqual(
            [
                block.content
                for block in answer.blocks
                if isinstance(block, EquationBlock)
            ],
            ["a = b", "b = c", "c = d"],
        )

    def test_equation_inside_key_idea_is_normalized(self):
        raw = """<KEY_IDEA>
Start with this identity.
<EQUATION>x + y = z</EQUATION>
Then interpret it.
</KEY_IDEA>
<EXPLANATION>A separate explanation.</EXPLANATION>"""

        answer = normalize_response(raw)

        self.assertEqual(answer.keyIdea, "Start with this identity.")
        self.assertIsNone(answer.explanation)
        self.assertEqual(
            [type(block) for block in answer.blocks],
            [EquationBlock, MarkdownBlock, MarkdownBlock],
        )
        self.assertEqual(answer.blocks[0].content, "x + y = z")
        self.assertEqual(answer.blocks[1].content, "Then interpret it.")
        self.assertEqual(answer.blocks[2].content, "A separate explanation.")

    def test_mathematical_equation_uses_generic_equation_block(self):
        raw = """<KEY_IDEA>A general relationship.</KEY_IDEA>
<EXPLANATION>Apply the relationship.</EXPLANATION>
<EXAMPLE title="Worked example">
Substitute the values.
<EQUATION>f(x) = x^2 + 2x + 1</EQUATION>
Evaluate the result.
</EXAMPLE>"""

        answer = normalize_response(raw)
        example = answer.blocks[0]

        self.assertIsInstance(example, ExampleBlock)
        self.assertTrue(any(isinstance(block, EquationBlock) for block in example.blocks))
        self.assertNotIn("<KEY_IDEA>", "".join(
            block.content
            for block in example.blocks
            if isinstance(block, MarkdownBlock)
        ))


if __name__ == "__main__":
    unittest.main()
