from rag.context import build_context


def test_build_context():
    chunks = [
        {
            "chunk_id": 4,
            "source": "Python_Interview_Preparation_Detailed.pdf",
            "text": "Lists are mutable sequences in Python.",
            "score": 0.68,
        },
        {
            "chunk_id": 14,
            "source": "Python_Interview_Preparation_Detailed.pdf",
            "text": "Decorators modify the behavior of functions.",
            "score": 0.64,
        },
    ]

    context = build_context(chunks)

    assert "[Context 1]" in context
    assert "[Context 2]" in context

    assert "Chunk ID: 4" in context
    assert "Chunk ID: 14" in context

    assert "Lists are mutable sequences in Python." in context
    assert "Decorators modify the behavior of functions." in context

    assert context.index("[Context 1]") < context.index("[Context 2]")


def test_build_context_with_no_chunks():
    assert build_context([]) == ""