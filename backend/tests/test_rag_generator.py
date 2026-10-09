from unittest.mock import patch

from rag.generator import generate_rag_answer


def test_generate_rag_answer():
    chunks = [
        {
            "chunk_id": 14,
            "source": "Python_Interview_Preparation_Detailed.pdf",
            "text": "A decorator modifies the behavior of a function.",
            "score": 0.61,
        }
    ]

    with patch("rag.generator.generate_text") as mock_generate:
        mock_generate.return_value = "A decorator modifies the behavior of a function."

        answer = generate_rag_answer(
            question="What is a Python decorator?",
            chunks=chunks,
        )

        assert answer == "A decorator modifies the behavior of a function."

        mock_generate.assert_called_once()

        prompt = mock_generate.call_args.args[0]

        assert "What is a Python decorator?" in prompt
        assert "A decorator modifies the behavior of a function." in prompt
        assert "retrieved context as the primary factual source" in prompt

def test_generate_rag_answer_without_context():
    with patch("rag.generator.generate_text") as mock_generate:
        try:
            generate_rag_answer(
                question="What is Python?",
                chunks=[],
            )
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert str(exc) == "No relevant context was retrieved."

        mock_generate.assert_not_called()
