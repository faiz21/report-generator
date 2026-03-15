from src.core.config import load_yaml_config


class MarkdownChunker:
    def __init__(self, config_path: str = "config/chunking.yaml"):
        config = load_yaml_config(config_path)
        recursive_config = config.get("recursive", {})
        self.chunk_size = recursive_config.get("chunk_size", 1500)
        self.chunk_overlap = recursive_config.get("chunk_overlap", 200)
        self.separators = recursive_config.get(
            "separators", ["\n## ", "\n### ", "\n\n", "\n", ". "]
        )

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        try:
            from langchain_text_splitters import (
                MarkdownHeaderTextSplitter,
                RecursiveCharacterTextSplitter,
            )

            # First split by markdown headers
            headers_to_split_on = [
                ("#", "h1"),
                ("##", "h2"),
            ]
            md_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=headers_to_split_on,
                strip_headers=False,
            )
            md_docs = md_splitter.split_text(text)

            # Then recursively split any oversized chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )

            chunks = []
            for doc in md_docs:
                content = doc.page_content
                if len(content) > self.chunk_size:
                    sub_chunks = text_splitter.split_text(content)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(content)

            return chunks if chunks else [text]

        except ImportError:
            # Fallback: simple split by double newlines
            parts = text.split("\n\n")
            return [p.strip() for p in parts if p.strip()]
