def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        if not chunk.get("text"):
            continue

        context_parts.append(
            f"""[Context {index}]
Source: {chunk.get("source", "Unknown")}
Chunk ID: {chunk.get("chunk_id", "Unknown")}

{chunk["text"]}"""
        )

    return "\n\n".join(context_parts)