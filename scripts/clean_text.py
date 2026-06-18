from pathlib import Path
import os
import re

input_root = Path("data/text")
output_root = Path("data/clean_text")
output_root.mkdir(exist_ok=True)

DEBUG_REPAIRS = (
    os.getenv("NCERT_CLEAN_DEBUG", "").lower()
    in {"1", "true", "yes", "on"}
)

ARROW_PATTERN = r"(?:\u2192|â†’|->|®)"

ELEMENTS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U",
}

CHEMISTRY_WORD_PATTERN = re.compile(
    (
        r"\b(acid|base|salt|chemical|reaction|formula|compound|"
        r"carbonate|hydrogencarbonate|hydroxide|sulphate|sulfate|"
        r"nitrate|oxide|chloride|bromide|iodide|ammonia|water|"
        r"reacts?|reactants?|products?)\b"
    ),
    flags=re.IGNORECASE
)

CHEMICAL_STATE_PATTERN = re.compile(
    r"\((?:aq|s|l|g)\)",
    flags=re.IGNORECASE
)

COMPACT_FORMULA_PATTERN = (
    r"(?:\d+)?(?:[A-Z][a-z]?\d*)+"
)


def log_repair(debug, message):
    if debug or DEBUG_REPAIRS:
        print(message)

def remove_consecutive_duplicates(lines):
    cleaned_lines = []
    previous_line = None

    for line in lines:
        line = line.strip()

        if line == previous_line:
            continue

        cleaned_lines.append(line)
        previous_line = line

    return cleaned_lines

def merge_broken_headings(lines):
    merged_lines = []
    i = 0

    while i < len(lines):
        current = lines[i].strip()

        if (
            current.isupper()
            and len(current) < 60
        ):
            while (
                i + 1 < len(lines)
                and lines[i + 1].strip().isupper()
                and len(lines[i + 1].strip()) < 60
            ):
                current += (
                    " "
                    + lines[i + 1].strip()
                )
                i += 1

        merged_lines.append(current)
        i += 1

    return merged_lines

def fix_split_title_words(lines):
    fixed_lines = []

    for line in lines:
        line = line.strip()

        if (
            line.isupper()
            and len(line) < 120
        ):
            words = line.split()
            rebuilt = []
            i = 0

            while i < len(words):
                if (
                    len(words[i]) == 1
                    and i + 1 < len(words)
                ):
                    rebuilt.append(
                        words[i]
                        + words[i + 1]
                    )
                    i += 2
                else:
                    rebuilt.append(
                        words[i]
                    )
                    i += 1

            line = " ".join(
                rebuilt
            )

        fixed_lines.append(
            line
        )

    return fixed_lines

def fix_broken_math_headings(lines):
    heading_fixes = {
        "R N EAL UMBERS":
            "REAL NUMBERS",
        "RN EAL UMBERS":
            "REAL NUMBERS",
        "P OLYNOMIALS":
            "POLYNOMIALS",
        "P AIR OF LINEAR EQUATIONS IN TWO VARIABLES":
            "PAIR OF LINEAR EQUATIONS IN TWO VARIABLES",
        "PLETV IN WO ARIABLES":
            "PAIR OF LINEAR EQUATIONS IN TWO VARIABLES",
        "QE UADRATIC QUATIONS":
            "QUADRATIC EQUATIONS",
        "QU ADRATIC EQUATIONS":
            "QUADRATIC EQUATIONS",
        "A P RITHMETIC ROGRESSIONS":
            "ARITHMETIC PROGRESSIONS",
        "AR ITHMETIC PROGRESSIONS":
            "ARITHMETIC PROGRESSIONS",
        "T RIANGLES":
            "TRIANGLES",
        "C OORDINATE GEOMETRY":
            "COORDINATE GEOMETRY",
        "I NTRODUCTION TO TRIGONOMETRY":
            "INTRODUCTION TO TRIGONOMETRY",
        "S OME APPLICATIONS OF TRIGONOMETRY":
            "SOME APPLICATIONS OF TRIGONOMETRY",
        "C IRCLES":
            "CIRCLES",
        "C ONSTRUCTIONS":
            "CONSTRUCTIONS",
        "A REAS RELATED TO CIRCLES":
            "AREAS RELATED TO CIRCLES",
        "S URFACE AREAS AND VOLUMES":
            "SURFACE AREAS AND VOLUMES",
        "S TATISTICS":
            "STATISTICS",
        "P ROBABILITY":
            "PROBABILITY"
    }

    fixed_lines = []

    for line in lines:
        line = line.strip()

        if line in heading_fixes:
            line = heading_fixes[line]

        fixed_lines.append(line)

    return fixed_lines

def fix_repeated_characters(text):
    text = re.sub(
        r"([A-Za-z])\1{2,}",
        r"\1",
        text
    )
    return text
def remove_ocr_garbage(text):

    garbage_patterns = [

        r"1111100000\.{2,}\d+",
        r"\?wonK uoY oD",
        r"AN ROTETOTHE EADER",
        r"Figure\s+\d+\.\d{5,}",
        r"Activity\s+\d+\.\d{5,}",

        r"\bREPRINT\s+\d{4}-\d{2}\b",

        r"\bPage\s+\d+\b",

        r"^\s*\d{6,}\s*$"
    ]

    for pattern in garbage_patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.MULTILINE
        )

    return text
def normalize_ocr_symbols(text):
    replacements = {
        "â€“": "-",
        "â€”": "-",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â„¦": "Ω",
        "â†’": "→",
        "Ã—": "×",
        "Â°": "°",
        "ï‚¹": "≠",
        "ï€½": "=",
        "ï‚£": "≤",
        "ï‚³": "≥",
        "": "=",
        "": "≠",
        "": "≤",
        "": "≥",
        "": "×",
        "": "+",
        "": "-",
        "": "÷",
        "": "π",
        "": "θ",
        "": "α",
        "": "β",
        "": "γ",
        "": "•",
        "": "Δ",
        "": "∠",
        "": "·",
        "": "(",
        "": ")",
        "": "(",
        "": ")",
        "": "(",
        "": ")",
        "": "-",
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new
        )

    return text

def fix_known_ocr_phrases(text):
    replacements = [
        (
            r"\bR\s*N\s*EAL\s+UMBERS\b",
            "REAL NUMBERS"
        ),
        (
            r"\bP\s+OLYNOMIALS\b",
            "POLYNOMIALS"
        ),
        (
            r"\bP\s+AIR\s+OF\s+LINEAR\s+EQUATIONS\s+IN\s+TWO\s+VARIABLES\b",
            "PAIR OF LINEAR EQUATIONS IN TWO VARIABLES"
        ),
        (
            r"\bPL\s+ET\s+V?\s*IN\s+WO\s+ARIABLES\b",
            "PAIR OF LINEAR EQUATIONS IN TWO VARIABLES"
        ),
        (
            r"\bPLETV\s+IN\s+WO\s+ARIABLES\b",
            "PAIR OF LINEAR EQUATIONS IN TWO VARIABLES"
        ),
        (
            r"\bQ\s*E\s+UADRATIC\s+QUATIONS\b",
            "QUADRATIC EQUATIONS"
        ),
        (
            r"\bA\s+P\s+RITHMETIC\s+ROGRESSIONS\b",
            "ARITHMETIC PROGRESSIONS"
        ),
        (
            r"\bAR\s+ITHMETIC\s+PROGRESSIONS\b",
            "ARITHMETIC PROGRESSIONS"
        ),
        (
            r"\bP\s+M\s+ROOFS\s+IN\s+ATHEMATICS\b",
            "PROOFS IN MATHEMATICS"
        ),
        (
            r"\?wonK uoY oD",
            "DO YOU KNOW?"
        ),

        (
            r"AN ROTETOTHE EADER",
            "A NOTE TO THE READER"
        ),
    ]

    for pattern, replacement in replacements:
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    return text

def parse_formula(value):
    value = re.sub(
        r"^\d+",
        "",
        value.strip()
    )

    if not value:
        return None

    def parse_until(index, terminator=None):
        element_count = 0
        has_subscript = False

        while index < len(value):
            char = value[index]

            if terminator and char == terminator:
                return index + 1, element_count, has_subscript

            if char == "(":
                parsed = parse_until(
                    index + 1,
                    ")"
                )

                if parsed is None:
                    return None

                index, inner_count, inner_subscript = parsed

                if inner_count == 0:
                    return None

                digit_match = re.match(
                    r"\d+",
                    value[index:]
                )

                if digit_match:
                    has_subscript = True
                    index += len(
                        digit_match.group(0)
                    )

                element_count += inner_count
                has_subscript = (
                    has_subscript
                    or inner_subscript
                )
                continue

            if not char.isupper():
                return None

            element = char
            index += 1

            if (
                index < len(value)
                and value[index].islower()
            ):
                element += value[index]
                index += 1

            if element not in ELEMENTS:
                return None

            digit_match = re.match(
                r"\d+",
                value[index:]
            )

            if digit_match:
                has_subscript = True
                index += len(
                    digit_match.group(0)
                )

            element_count += 1

        if terminator:
            return None

        return index, element_count, has_subscript

    parsed = parse_until(0)

    if parsed is None:
        return None

    index, element_count, has_subscript = parsed

    if index != len(value):
        return None

    return element_count, has_subscript

def is_valid_formula(value, require_subscript=False):
    parsed = parse_formula(
        value
    )

    if not parsed:
        return False

    element_count, has_subscript = parsed

    if require_subscript and not has_subscript:
        return False

    return element_count > 0

def has_spaced_formula_pattern(line):
    return bool(
        re.search(
            r"(?:[A-Z][a-z]?|[A-Z]{2,})\s+\d",
            line
        )
        or re.search(
            r"\d+\s+(?:[A-Z][a-z]?|[A-Z]{2,})",
            line
        )
    )

def looks_like_formula_line(line):
    stripped = line.strip()

    if not stripped:
        return False

    if re.fullmatch(
        r"[A-Z]\s+(?:\d+\s*){2,}",
        stripped
    ):
        return False

    if not re.fullmatch(
        r"[\dA-Za-z\s()+\-.,=+]*",
        stripped
    ):
        return False

    return (
        has_spaced_formula_pattern(stripped)
        and len(re.findall(r"[A-Z]", stripped)) >= 2
    )

def is_chemical_context_line(line):
    return bool(
        re.search(ARROW_PATTERN, line)
        or CHEMICAL_STATE_PATTERN.search(line)
        or (
            "+" in line
            and re.search(r"\b[A-Z][a-z]?\b", line)
        )
        or CHEMISTRY_WORD_PATTERN.search(line)
        or looks_like_formula_line(line)
    )

def repair_formula_spacing_in_line(line):
    if not is_chemical_context_line(line):
        return line

    def attach_digit(match):
        token = match.group(1)
        digit = match.group(2)
        compact = token + digit

        if is_valid_formula(
            compact,
            require_subscript=True
        ):
            return compact

        return match.group(0)

    def attach_parenthesis_digit(match):
        compact = match.group(1) + match.group(2)

        if is_valid_formula(
            compact,
            require_subscript=True
        ):
            return compact

        return match.group(0)

    def join_formula_pair(match):
        first = match.group(1)
        second = match.group(2)
        compact = first + second
        without_coefficient = re.sub(
            r"^\d+",
            "",
            compact
        )

        if (
            re.search(r"\d", without_coefficient)
            and is_valid_formula(compact)
        ):
            return compact

        return match.group(0)

    previous = None

    while previous != line:
        previous = line

        line = re.sub(
            r"(?<![A-Za-z])((?:[A-Z][a-z]?)+)\s+(\d+)\b",
            attach_digit,
            line
        )

        line = re.sub(
            r"(\((?:[A-Z][a-z]?\d*)+\))\s+(\d+)\b",
            attach_parenthesis_digit,
            line
        )

        line = re.sub(
            (
                r"(?<![A-Za-z])"
                rf"({COMPACT_FORMULA_PATTERN})"
                r"\s+"
                rf"({COMPACT_FORMULA_PATTERN})"
                r"(?![a-z])"
            ),
            join_formula_pair,
            line
        )

    return line

def repair_formula_spacing(text):
    return "\n".join(
        repair_formula_spacing_in_line(line)
        for line in text.splitlines()
    )

def should_append_compact_subscript(compact):
    formula = re.sub(
        r"^\d+",
        "",
        compact
    )

    if re.search(
        r"(SO|CO|NO|HCO|O)$",
        formula
    ):
        return True

    if re.search(
        r"(Cl|Br|I)$",
        formula
    ):
        first_element = re.match(
            r"[A-Z][a-z]?",
            formula
        )

        if not first_element:
            return False

        return first_element.group(0) not in {
            "H", "Na", "K", "Ag"
        }

    return False

def repair_chemical_formulas(text):
    patterns = [
        (
            r"H\s+SO\s*\n\s*2\s*4",
            "H2SO4"
        ),
        (
            r"HNO\s*\n\s*3",
            "HNO3"
        ),
        (
            r"CH\s*COOH\s*\n\s*3",
            "CH3COOH"
        ),
        (
            r"CH\s*CH\s*OH\s*\n\s*3\s*2",
            "CH3CH2OH"
        ),
        (
            r"Mg\(OH\)\s*\n\s*2",
            "Mg(OH)2"
        ),
        (
            r"Ca\(OH\)\s*\n\s*2",
            "Ca(OH)2"
        ),
        (
            r"NH\s*\n\s*4OH",
            "NH4OH"
        )
    ]

    for pattern, replacement in patterns:
        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.MULTILINE
        )

    return text

def fix_ocr_numbering(text):

    def replacement(match):

        left = match.group(1)[0]
        right = match.group(2)[0]

        return f"{left}.{right}"

    # Existing fix:
    # 11111.....22222 -> 1.2

    text = re.sub(
        r"([1-9])\1{4}\.*([1-9])\2{4}",
        replacement,
        text
    )

    # Fix spaces around numbering

    text = re.sub(
        r"(\d)\s*\.\s*(\d)",
        r"\1.\2",
        text
    )

    # ---------------------------------
    # NEW FIXES
    # ---------------------------------

    # 1.1.....11111 -> 1.1

    text = re.sub(
        r"(\d+\.\d+)\.{2,}\d{5,}",
        r"\1",
        text
    )

    # Figure 1111100000.....11111
    # Figure 1.1

    text = re.sub(
        r"Figure\s+1111100000\.{2,}11111",
        "Figure 1.1",
        text
    )

    # Activity 1.2.....11111
    # Activity 1.2

    text = re.sub(
        r"(Activity\s+\d+\.\d+)\.{2,}\d{5,}",
        r"\1",
        text
    )

    # Question 1.1.....11111
    # Question 1.1

    text = re.sub(
        r"(Question\s+\d+\.\d+)\.{2,}\d{5,}",
        r"\1",
        text,
        flags=re.IGNORECASE
    )

    return text
def fix_figure_and_activity_numbers(text):

    current_chapter = None

    lines = text.splitlines()

    fixed_lines = []

    chapter_pattern = re.compile(
        r"^CHAPTER\s+(\d+)$",
        re.IGNORECASE
    )

    figure_pattern = re.compile(
        r"Figure\s+1\.(\d+)",
        re.IGNORECASE
    )

    activity_pattern = re.compile(
        r"Activity\s+1\.(\d+)",
        re.IGNORECASE
    )

    for line in lines:

        line = line.strip()

        chapter_match = chapter_pattern.match(
            line
        )

        if chapter_match:

            current_chapter = (
                chapter_match.group(1)
            )

        if current_chapter:

            line = figure_pattern.sub(
                rf"Figure {current_chapter}.\1",
                line
            )

            line = activity_pattern.sub(
                rf"Activity {current_chapter}.\1",
                line
            )

        fixed_lines.append(
            line
        )

    return "\n".join(
        fixed_lines
    )

def attach_trailing_formula_digit(line, digit):
    def replace_compact(match):
        formula = match.group("formula")
        punct = match.group("punct") or ""
        compact = formula + digit

        if (
            is_valid_formula(
                compact,
                require_subscript=True
            )
            and is_chemical_context_line(line)
        ):
            return compact + punct

        return match.group(0)

    fixed = re.sub(
        (
            r"(?P<formula>"
            r"(?:[A-Z][a-z]?)+"
            r"(?:SO|CO|NO|HCO|Cl|Br|I|O)"
            r")\s*(?P<punct>[.,;:]?)$"
        ),
        replace_compact,
        line
    )

    if fixed != line:
        return fixed

    def replace_parenthesised(match):
        formula = match.group("formula")
        punct = match.group("punct") or ""
        compact = formula + digit

        if (
            is_valid_formula(
                compact,
                require_subscript=True
            )
            and is_chemical_context_line(line)
        ):
            return compact + punct

        return match.group(0)

    return re.sub(
        (
            r"(?P<formula>"
            r"(?:[A-Z][a-z]?)+"
            r"\((?:[A-Z][a-z]?)+\)"
            r")\s*(?P<punct>[.,;:]?)$"
        ),
        replace_parenthesised,
        line
    )

def repair_split_formula_numbers(text):
    lines = text.splitlines()
    fixed_lines = []
    i = 0

    while i < len(lines):
        current = lines[i].rstrip()

        if (
            i + 1 < len(lines)
            and re.fullmatch(
                r"\d",
                lines[i + 1].strip()
            )
        ):
            fixed = attach_trailing_formula_digit(
                current,
                lines[i + 1].strip()
            )

            if fixed != current:
                fixed_lines.append(fixed)
                i += 2
                continue

        fixed_lines.append(current)
        i += 1

    return "\n".join(fixed_lines)

def normalize_scientific_notation(text):
    text = re.sub(
        r"(\b\d(?:\.\d+)?\s*(?:x|\u00d7)\s*)10([+-]?\d+)\b",
        r"\g<1>10^\2",
        text,
        flags=re.IGNORECASE
    )

    return text

def is_math_context(lines):
    context = " ".join(
        line.strip()
        for line in lines
        if line.strip()
    )

    return bool(
        re.search(
            (
                r"(=|/|\^|[+\-*]|\u00d7|"
                r"\b(rational|integer|integers|fraction|"
                r"denominator|numerator|where|form|ratio|"
                r"sin|cos|tan|cot|sec|cosec|hcf|lcm|"
                r"factorisation|resistance|resistor|current|"
                r"voltage|ohm|parallel)\b)"
            ),
            context,
            flags=re.IGNORECASE
        )
    )

def clean_math_part(value):
    return value.strip().strip(" ,.;:()[]{}")

def is_simple_math_part(value):
    value = clean_math_part(
        value
    )

    if not value or len(value) > 8:
        return False

    return bool(
        re.fullmatch(
            (
                r"(?:[A-Za-z]\d*|"
                r"\d+(?:\.\d+)?[A-Za-z]*|"
                r"[A-Za-z]\d+)"
            ),
            value
        )
    )

def split_math_row(line):
    parts = [
        clean_math_part(part)
        for part in line.strip().split()
    ]

    if (
        not parts
        or len(parts) > 6
        or any(
            not is_simple_math_part(part)
            for part in parts
        )
    ):
        return None

    return parts

def line_starts_with_math_part(line):
    match = re.match(
        (
            r"^\s*"
            r"([A-Za-z]\d*|\d+(?:\.\d+)?[A-Za-z]*|[A-Za-z]\d+)"
            r"(?=\s|[,.;:)]|$)"
            r"(.*)$"
        ),
        line.strip()
    )

    if not match:
        return None

    part = clean_math_part(
        match.group(1)
    )

    if not is_simple_math_part(part):
        return None

    return part, match.group(2)

def format_fraction_row(numerators, denominators):
    return " ".join(
        f"{numerator}/{denominator}"
        for numerator, denominator in zip(
            numerators,
            denominators
        )
    )

def is_equation_reference(line):
    return bool(
        re.fullmatch(
            r"\(\d+(?:\.\d+)+\)",
            line.strip()
        )
    )

def parse_subscript_row(line):
    tokens = line.strip().split()
    subscripts = []
    i = 0

    while i < len(tokens):
        token = clean_math_part(
            tokens[i]
        )

        if not token:
            i += 1
            continue

        if (
            i + 2 < len(tokens)
            and re.fullmatch(
                r"[A-Za-z0-9]+",
                token
            )
            and tokens[i + 1] in {"+", "-"}
            and re.fullmatch(
                r"[A-Za-z0-9]+",
                clean_math_part(tokens[i + 2])
            )
        ):
            subscripts.append(
                token
                + tokens[i + 1]
                + clean_math_part(tokens[i + 2])
            )
            i += 3
            continue

        if not re.fullmatch(
            r"[A-Za-z0-9]+",
            token
        ):
            return None

        subscripts.append(token)
        i += 1

    return subscripts

def format_subscripted_variable(variable, subscript):
    if re.search(
        r"[+-]",
        subscript
    ):
        return f"{variable}({subscript})"

    return f"{variable}{subscript}"

def merge_subscript_row(base_line, subscript_line):
    subscripts = parse_subscript_row(
        subscript_line
    )

    if (
        not subscripts
        or len(subscripts) < 2
        or len(subscripts) > 8
    ):
        return None

    variables = re.findall(
        r"\b([A-Za-z])\b",
        base_line
    )

    candidates = []

    for variable in sorted(set(variables)):
        if variables.count(variable) == len(subscripts):
            candidates.append(variable)

    if not candidates:
        return None

    variable = candidates[0]
    index = 0

    def replacement(match):
        nonlocal index

        value = format_subscripted_variable(
            match.group(0),
            subscripts[index]
        )
        index += 1
        return value

    return re.sub(
        rf"\b{re.escape(variable)}\b",
        replacement,
        base_line,
        count=len(subscripts)
    )

def merge_known_single_subscript(base_line, subscript_line):
    subscript = clean_math_part(
        subscript_line
    )

    if subscript != "p":
        return None

    if re.search(r"/R\b", base_line):
        return re.sub(
            r"/R\b",
            "/Rp",
            base_line,
            count=1
        )

    if re.search(
        r"\bR\b.*\bequivalent resistance\b",
        base_line,
        flags=re.IGNORECASE
    ):
        return re.sub(
            r"\bR\b",
            "Rp",
            base_line,
            count=1
        )

    return None

def merge_chemical_subscript_line(base_line, subscript_line):
    if not re.fullmatch(
        r"(?:\d+\s*){1,10}",
        subscript_line.strip()
    ):
        return None

    if not re.search(
        (
            r"(→|H\s+SO|HNO|CH\s+COOH|Ca\(OH\)|Mg\(OH\)|"
            r"NH\s+OH|Na\s+SO|H\s+O|ZnSO|BaSO|AgNO|NaNO|"
            r"NO\s*\)|SO\b|CO\b|O\b)"
        ),
        base_line
    ):
        return None

    digits = subscript_line.strip().split()
    used = 0

    def pop_digit():
        nonlocal used

        if used >= len(digits):
            return None

        digit = digits[used]
        used += 1
        return digit

    def replace_formula(match):
        value = match.group(0)

        if re.fullmatch(r"\(NO\s*\)", value):
            inner = pop_digit()
            outer = pop_digit()

            if inner is None or outer is None:
                return value

            return f"(NO{inner}){outer}"

        oh_group = re.fullmatch(
            r"(Ca|Mg)\(OH\)",
            value
        )

        if oh_group:
            outer = pop_digit()

            if outer is None:
                return value

            return f"{oh_group.group(1)}(OH){outer}"

        if value == "NH OH":
            digit = pop_digit()

            if digit is None:
                return value

            return f"NH{digit}OH"

        spaced = re.fullmatch(
            r"(H|Na|CH)\s+(SO|COOH|O)",
            value
        )

        if spaced:
            first = spaced.group(1)
            second = spaced.group(2)

            if second in {"COOH", "O"}:
                digit = pop_digit()

                if digit is None:
                    return value

                return f"{first}{digit}{second}"

            first_digit = pop_digit()
            second_digit = pop_digit()

            if first_digit is None or second_digit is None:
                return value

            return f"{first}{first_digit}{second}{second_digit}"

        digit = pop_digit()

        if digit is None:
            return value

        return f"{value}{digit}"

    line = re.sub(
        (
            r"\(NO\s*\)|"
            r"\b(?:Ca|Mg)\(OH\)|"
            r"\bNH\s+OH\b|"
            r"\b(?:H|Na|CH)\s+(?:SO|COOH|O)\b|"
            r"\b(?:HNO|ZnSO|NaNO|AgNO|BaSO|CuSO|FeSO|NaSO|H|O)\b"
        ),
        replace_formula,
        base_line
    )

    if used == 0:
        return None

    return line

def merge_chemical_subscript_line(base_line, subscript_line):
    if not re.fullmatch(
        r"(?:\d+\s*){1,10}",
        subscript_line.strip()
    ):
        return None

    if not is_chemical_context_line(base_line):
        return None

    digits = subscript_line.strip().split()
    used = 0

    def pop_digit():
        nonlocal used

        if used >= len(digits):
            return None

        digit = digits[used]
        used += 1
        return digit

    def remaining_digits():
        return len(digits) - used

    def replace_formula(match):
        value = match.group(0)

        parenthetical_group = match.group("parenthetical_group")

        if parenthetical_group:
            inner = pop_digit()

            if inner is None:
                return value

            repaired = (
                "("
                + parenthetical_group
                + inner
                + ")"
            )

            outer = pop_digit()

            if outer is not None:
                repaired += outer

            return repaired

        hydroxide_owner = match.group("hydroxide_owner")

        if hydroxide_owner:
            outer = pop_digit()

            if outer is None:
                return value

            return f"{hydroxide_owner}(OH){outer}"

        ammonium_group = match.group("ammonium_group")

        if ammonium_group:
            digit = pop_digit()

            if digit is None:
                return value

            return f"NH{digit}{ammonium_group}"

        ethyl_suffix = match.group("ethyl_suffix")

        if ethyl_suffix:
            first_digit = pop_digit()
            second_digit = pop_digit()

            if first_digit is None or second_digit is None:
                return value

            coefficient = match.group("ethyl_coefficient") or ""

            return (
                f"{coefficient}CH{first_digit}"
                f"CH{second_digit}{ethyl_suffix}"
            )

        methyl_group = match.group("methyl_group")

        if methyl_group:
            digit = pop_digit()

            if digit is None:
                return value

            coefficient = match.group("methyl_coefficient") or ""

            return f"{coefficient}CH{digit}{methyl_group}"

        hydride = match.group("hydride")

        if hydride:
            digit = pop_digit()

            if digit is None:
                return value

            return hydride + digit

        prefix = match.group("prefix")
        oxo_group = match.group("oxo_group")

        if prefix and oxo_group:
            first_digit = pop_digit()
            second_digit = pop_digit()

            if first_digit is None or second_digit is None:
                return value

            return (
                f"{prefix}{first_digit}"
                f"{oxo_group}{second_digit}"
            )

        oxide_prefix = match.group("oxide_prefix")

        if oxide_prefix:
            first_digit = pop_digit()

            if first_digit is None:
                return value

            if oxide_prefix == "H":
                return f"H{first_digit}O"

            if remaining_digits() > 0:
                second_digit = pop_digit()
                return (
                    f"{oxide_prefix}{first_digit}"
                    f"O{second_digit}"
                )

            return f"{oxide_prefix}O{first_digit}"

        compact = match.group("compact")

        if compact:
            if not should_append_compact_subscript(
                compact
            ):
                return value

            digit = pop_digit()

            if digit is None:
                return value

            return compact + digit

        molecule = match.group("molecule")

        if molecule:
            digit = pop_digit()

            if digit is None:
                return value

            return molecule + digit

        return value

    line = re.sub(
        (
            r"\((?P<parenthetical_group>NO|SO|CO|HCO)\s*\)|"
            r"\b(?P<hydroxide_owner>[A-Z][a-z]?)\(OH\)|"
            r"\bNH\s+(?P<ammonium_group>Cl|OH)\b|"
            r"(?<![A-Za-z])(?P<ethyl_coefficient>\d*)"
            r"CH\s+CH\s+(?P<ethyl_suffix>OH|O\S*Na\+)|"
            r"(?<![A-Za-z])(?P<methyl_coefficient>\d*)"
            r"CH\s+(?P<methyl_group>COOH|COONa)\b|"
            r"\b(?P<hydride>CH|NH)\b|"
            r"\b(?P<prefix>[A-Z][a-z]?)\s+"
            r"(?P<oxo_group>SO|CO|NO|HCO)\b|"
            r"\b(?P<oxide_prefix>[A-Z][a-z]?)\s+O\b|"
            r"\b(?P<compact>"
            r"(?:[A-Z][a-z]?)+"
            r"(?:SO|CO|NO|HCO|Cl|Br|I|O)"
            r")\b|"
            r"\b(?P<molecule>H|O|N|Cl)\b"
        ),
        replace_formula,
        base_line
    )

    if used == 0 or used != len(digits):
        return None

    return repair_formula_spacing_in_line(line)

def repair_broken_math_lines(lines, debug=False):
    fixed_lines = []
    i = 0

    while i < len(lines):
        current = lines[i].strip()

        if not current:
            fixed_lines.append(current)
            i += 1
            continue

        if is_equation_reference(current):
            fixed_lines.append(current)
            i += 1
            continue

        next_line = (
            lines[i + 1].strip()
            if i + 1 < len(lines)
            else ""
        )

        if next_line:
            chemical_merged = merge_chemical_subscript_line(
                current,
                next_line
            )

            if chemical_merged:
                log_repair(
                    debug,
                    (
                        "Merged chemical subscripts: "
                        f"{current} / {next_line} -> "
                        f"{chemical_merged}"
                    )
                )
                fixed_lines.append(
                    chemical_merged
                )
                i += 2
                continue

        if next_line:
            sci_match = re.search(
                r"((?:x|\u00d7)\s*10)\s*$",
                current,
                flags=re.IGNORECASE
            )

            exp_match = re.match(
                r"^([+-]?\d+)(\b.*)$",
                next_line
            )

            if sci_match and exp_match:
                merged = (
                    current
                    + "^"
                    + exp_match.group(1)
                    + exp_match.group(2)
                ).strip()
                log_repair(
                    debug,
                    (
                        "Merged scientific notation: "
                        f"{current} / {next_line} -> {merged}"
                    )
                )
                fixed_lines.append(
                    merged
                )
                i += 2
                continue

        if (
            i + 3 < len(lines)
            and re.fullmatch(r"[A-Za-z]", current)
            and re.fullmatch(r"\d+", next_line)
            and lines[i + 2].strip() == current
            and re.fullmatch(
                r"\d+",
                lines[i + 3].strip()
            )
        ):
            first = current + next_line
            second = (
                lines[i + 2].strip()
                + lines[i + 3].strip()
            )
            log_repair(
                debug,
                (
                    "Merged split math symbols: "
                    f"{current} / {next_line} and "
                    f"{lines[i + 2].strip()} / "
                    f"{lines[i + 3].strip()} -> "
                    f"{first}, {second}"
                )
            )
            fixed_lines.append(
                first
            )
            fixed_lines.append(
                second
            )
            i += 4
            continue

        if next_line:
            single_subscript_merged = merge_known_single_subscript(
                current,
                next_line
            )

            if single_subscript_merged:
                log_repair(
                    debug,
                    (
                        "Merged single subscript: "
                        f"{current} / {next_line} -> "
                        f"{single_subscript_merged}"
                    )
                )
                fixed_lines.append(
                    single_subscript_merged
                )
                i += 2
                continue

            subscript_merged = merge_subscript_row(
                current,
                next_line
            )

            if subscript_merged:
                log_repair(
                    debug,
                    (
                        "Merged subscript row: "
                        f"{current} / {next_line} -> "
                        f"{subscript_merged}"
                    )
                )
                fixed_lines.append(
                    subscript_merged
                )
                i += 2
                continue

        current_parts = split_math_row(
            current
        )

        if (
            current_parts
            and i + 2 < len(lines)
        ):
            middle = lines[i + 1].strip()
            denominator_parts = split_math_row(
                lines[i + 2].strip()
            )

            if (
                denominator_parts
                and len(current_parts) == len(denominator_parts)
                and is_math_context(
                    lines[
                        max(0, i - 2):
                        min(len(lines), i + 5)
                    ]
                )
            ):
                merged = (
                    (
                        format_fraction_row(
                            current_parts,
                            denominator_parts
                        )
                        + " "
                        + middle
                    ).strip()
                )
                log_repair(
                    debug,
                    (
                        "Merged fraction row: "
                        f"{current_parts} / {denominator_parts} "
                        f"with middle '{middle}' -> {merged}"
                    )
                )
                fixed_lines.append(
                    merged
                )
                i += 3
                continue

        if (
            current_parts
            and len(current_parts) == 1
            and next_line
        ):
            next_start = line_starts_with_math_part(
                next_line
            )

            if next_start:
                denominator, rest = next_start

            if (
                next_start
                and not (
                    current_parts[0][0].isdigit()
                    and denominator[0].isalpha()
                )
                and is_math_context(
                    lines[
                        max(0, i - 2):
                        min(len(lines), i + 4)
                    ]
                )
            ):
                skip_count = 2

                if (
                    i + 2 < len(lines)
                    and clean_math_part(
                        lines[i + 2]
                    ) == denominator
                ):
                    skip_count = 3

                merged = (
                    f"{current_parts[0]}/{denominator}"
                    + rest
                ).strip()
                log_repair(
                    debug,
                    (
                        "Merged fraction: "
                        f"{current_parts[0]} / {denominator} -> "
                        f"{merged}"
                    )
                )
                fixed_lines.append(
                    merged
                )
                i += skip_count
                continue

        next_parts = split_math_row(
            next_line
        )

        if (
            current_parts
            and next_parts
            and len(current_parts) == len(next_parts)
            and is_math_context(
                lines[
                    max(0, i - 2):
                    min(len(lines), i + 4)
                ]
            )
        ):
            merged = format_fraction_row(
                current_parts,
                next_parts
            )
            log_repair(
                debug,
                (
                    "Merged fraction row: "
                    f"{current_parts} / {next_parts} -> "
                    f"{merged}"
                )
            )
            fixed_lines.append(
                merged
            )
            i += 2
            continue

        fixed_lines.append(current)
        i += 1

    return fixed_lines

def repair_chemical_equations(text):
    replacements = {
        "Zn + HCl → ZnCl + H 2 2":
            "Zn + 2HCl → ZnCl2 + H2",
        "Mg + O 2 → MgO":
            "Mg + O2 → MgO",
        "2Mg + O 2 → 2MgO":
            "2Mg + O2 → 2MgO",
        "Fe + CuSO 4 → FeSO 4 + Cu":
            "Fe + CuSO4 → FeSO4 + Cu",
        "BaCl 2 + Na SO 2 4":
            "BaCl2 + Na2SO4"
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new
        )

    return text
def normalize_common_chemistry_ocr(text):

    replacements = {

        # Common NCERT chemistry equations

        "CaO2(s)": "CaO(s)",
        "CaO2 (s)": "CaO (s)",

        "Ca(OH) (aq)": "Ca(OH)2(aq)",
        "Ca(OH)2 (aq)": "Ca(OH)2(aq)",

        "CuO2 +H2": "CuO + H2",
        "CuO2 + H2": "CuO + H2",

        "H O(l)": "H2O(l)",
        "H O (l)": "H2O(l)",

        "H O(g)": "H2O(g)",
        "H O (g)": "H2O(g)",

        "FeSO 4": "FeSO4",
        "CuSO 4": "CuSO4",
        "ZnSO 4": "ZnSO4",
        "BaSO 4": "BaSO4",

        "H2 SO4": "H2SO4",
        "Na2 SO4": "Na2SO4",

        "Pb(NO )": "Pb(NO3)",
        "FeSO (s)": "FeSO4(s)",

        "SO (g)": "SO2(g)",
        "SO (aq)": "SO2(aq)",

        "NO (g)": "NO2(g)",
        "NO )": "NO2)",

        "CO (g)": "CO2(g)",
        "CO (aq)": "CO2(aq)"
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    return text

def repair_chemical_equations(text):
    return repair_formula_spacing(text)

def is_chemical_equation_fragment(line):
    stripped = line.strip()

    if not stripped or len(stripped) > 160:
        return False

    return bool(
        re.search(ARROW_PATTERN, stripped)
        or CHEMICAL_STATE_PATTERN.search(stripped)
        or (
            "+" in stripped
            and re.search(
                COMPACT_FORMULA_PATTERN,
                stripped
            )
        )
        or re.search(
            r"\b[A-Z][a-z]?\d+[A-Z]?",
            stripped
        )
    )

def normalize_equation_line(line):
    line = re.sub(
        r"\s+",
        " ",
        line
    ).strip()

    return repair_formula_spacing_in_line(line)

def merge_multiline_equations(lines, debug=False):
    fixed_lines = []
    i = 0
    arrow_only_pattern = re.compile(
        rf"^{ARROW_PATTERN}$"
    )
    arrow_start_pattern = re.compile(
        rf"^{ARROW_PATTERN}\s*"
    )

    while i < len(lines):
        current = lines[i].strip()
        next_line = (
            lines[i + 1].strip()
            if i + 1 < len(lines)
            else ""
        )

        if (
            current
            and next_line
            and is_chemical_equation_fragment(current)
            and arrow_only_pattern.fullmatch(next_line)
            and i + 2 < len(lines)
            and is_chemical_equation_fragment(lines[i + 2])
        ):
            merged = normalize_equation_line(
                current
                + " "
                + next_line
                + " "
                + lines[i + 2].strip()
            )
            log_repair(
                debug,
                (
                    "Merged multiline equation: "
                    f"{current} / {next_line} / "
                    f"{lines[i + 2].strip()} -> {merged}"
                )
            )
            fixed_lines.append(merged)
            i += 3
            continue

        if (
            current
            and next_line
            and is_chemical_equation_fragment(current)
            and arrow_start_pattern.match(next_line)
        ):
            merged = normalize_equation_line(
                current
                + " "
                + next_line
            )
            log_repair(
                debug,
                (
                    "Merged multiline equation: "
                    f"{current} / {next_line} -> {merged}"
                )
            )
            fixed_lines.append(merged)
            i += 2
            continue

        if (
            current.endswith("+")
            and next_line
            and is_chemical_equation_fragment(current)
            and is_chemical_equation_fragment(next_line)
        ):
            merged = normalize_equation_line(
                current
                + " "
                + next_line
            )
            log_repair(
                debug,
                (
                    "Merged wrapped equation line: "
                    f"{current} / {next_line} -> {merged}"
                )
            )
            fixed_lines.append(merged)
            i += 2
            continue

        fixed_lines.append(current)
        i += 1

    return fixed_lines

def parse_two_column_table_row(line):
    stripped = line.strip()

    patterns = [
        r"^(Below\s+\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?|[A-Za-z])$",
        r"^(Above\s+\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?|[A-Za-z])$",
        r"^(Less than\s+\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?|[A-Za-z])$",
        r"^(More than\s+\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?|[A-Za-z])$",
        r"^(\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?|[A-Za-z])$",
        r"^(Total)\s+(\d+(?:\.\d+)?|[A-Za-z])$",
        r"^(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?|[A-Za-z])$",
    ]

    for pattern in patterns:
        match = re.fullmatch(
            pattern,
            stripped,
            flags=re.IGNORECASE
        )

        if match:
            return (
                re.sub(r"\s+", " ", match.group(1)).strip(),
                match.group(2).strip()
            )

    return None

def split_two_column_header(line):
    stripped = re.sub(
        r"\s+",
        " ",
        line.strip()
    )

    if (
        not re.search(r"[A-Za-z]", stripped)
        or re.search(r"[.?:;]$", stripped)
    ):
        return None

    if re.match(
        r"^\d+\s+(SCIENCE|MATHEMATICS)$",
        stripped,
        flags=re.IGNORECASE
    ):
        return None

    number_markers = list(
        re.finditer(
            r"\bNumber of\b",
            stripped
        )
    )

    if len(number_markers) >= 2:
        split_at = number_markers[-1].start()
        return (
            stripped[:split_at].strip(),
            stripped[split_at:].strip()
        )

    marker_match = re.search(
        r"\bNumber of\b",
        stripped
    )

    if marker_match and marker_match.start() > 0:
        return (
            stripped[:marker_match.start()].strip(),
            stripped[marker_match.start():].strip()
        )

    for marker in [
        " Frequency",
        " Pairs of",
    ]:
        index = stripped.find(marker)

        if index > 0:
            return (
                stripped[:index].strip(),
                stripped[index + 1:].strip()
            )

    first_column_words = {
        "Age", "Class", "Height", "Length", "Marks",
        "Month", "Runs", "Weight",
    }

    words = stripped.split(maxsplit=1)

    if (
        len(words) == 2
        and words[0] in first_column_words
        and words[1][0].isupper()
    ):
        return words[0], words[1]

    return None

def normalize_two_column_tables(lines, debug=False):
    fixed_lines = []
    i = 0

    while i < len(lines):
        header = split_two_column_header(
            lines[i]
        )

        if header:
            rows = []
            j = i + 1

            while j < len(lines):
                row = parse_two_column_table_row(
                    lines[j]
                )

                if not row:
                    break

                rows.append(row)
                j += 1

            if len(rows) >= 2:
                header_line = (
                    f"{header[0]} | {header[1]}"
                )
                log_repair(
                    debug,
                    (
                        "Formatted two-column table: "
                        f"{lines[i].strip()} with "
                        f"{len(rows)} rows"
                    )
                )
                fixed_lines.append(header_line)

                for left, right in rows:
                    fixed_lines.append(
                        f"{left} | {right}"
                    )

                i = j
                continue

        fixed_lines.append(
            lines[i].strip()
        )
        i += 1

    return fixed_lines

def fix_ocr_page_numbers(lines):
    cleaned = []

    for line in lines:
        line = line.strip()

        if re.fullmatch(
            r"\d{5,}",
            line
        ):
            continue

        line = re.sub(
            r"Activity\s+1\.100000",
            "Activity 1.10",
            line
        )

        line = re.sub(
            r"Activity\s+1\.111111",
            "Activity 1.11",
            line
        )

        line = re.sub(
            r"Activity\s+1\.122222",
            "Activity 1.12",
            line
        )

        cleaned.append(line)

    return cleaned

def remove_page_headers_footers(lines):
    cleaned = []

    for line in lines:
        line = line.strip()

        if re.match(
            r"^\d+\s+(SCIENCE|MATHEMATICS)$",
            line,
            re.IGNORECASE
        ):
            continue

        if re.match(
            r"^[A-Z\s]+\s+\d+\s+[A-Z\s]+$",
            line
        ):
            continue

        if re.match(
            r"^[A-Za-z\s]+\s+\d+$",
            line
        ):
            continue

        cleaned.append(line)

    return cleaned

def clean_text(text, debug=False):
    text = fix_repeated_characters(
        text
    )
    text = remove_ocr_garbage(
        text
    )
    text = fix_ocr_numbering(
        text
    )
    text = fix_figure_and_activity_numbers(
        text
    )
    text = repair_chemical_formulas(
        text
    )

    text = repair_formula_spacing(
        text
    )

    text = repair_split_formula_numbers(
        text
    )

    text = normalize_scientific_notation(
        text
    )

    text = repair_chemical_equations(
        text
    )
    text = normalize_common_chemistry_ocr(
        text
    )
    text = re.sub(
        r"Reprint\s+\d{4}-\d{2}",
        "",
        text
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n\s*\n",
        "\n\n",
        text
    )

    lines = text.splitlines()

    lines = repair_broken_math_lines(
        lines,
        debug=debug
    )

    lines = merge_multiline_equations(
        lines,
        debug=debug
    )

    lines = normalize_two_column_tables(
        lines,
        debug=debug
    )

    lines = fix_ocr_page_numbers(
        lines
    )

    lines = remove_page_headers_footers(
        lines
    )

    lines = [
        line
        for line in lines
        if not re.match(
            r"^\d+\s+(Science|Mathematics)$",
            line.strip()
        )
    ]

    lines = [
        line
        for line in lines
        if not re.match(
            r"^\d+$",
            line.strip()
        )
    ]

    lines = remove_consecutive_duplicates(
        lines
    )

    lines = merge_broken_headings(
        lines
    )

    lines = fix_split_title_words(
        lines
    )

    lines = fix_broken_math_headings(
        lines
    )

    text = "\n".join(
        lines
    )

    text = repair_formula_spacing(
        text
    )

    return text.strip()


def clean_all(debug=False):
    for subject_folder in input_root.iterdir():
        if not subject_folder.is_dir():
            continue

        subject_output = (
            output_root /
            subject_folder.name
        )

        subject_output.mkdir(
            exist_ok=True
        )

        for txt_file in subject_folder.glob("*.txt"):
            text = txt_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            cleaned = clean_text(
                text,
                debug=debug
            )

            output_file = (
                subject_output /
                txt_file.name
            )

            output_file.write_text(
                cleaned,
                encoding="utf-8"
            )

            print(
                f"Cleaned: {txt_file.name}"
            )

    print("Cleaning complete.")

if __name__ == "__main__":
    clean_all(debug=DEBUG_REPAIRS)
