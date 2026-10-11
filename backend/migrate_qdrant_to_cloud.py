
from qdrant_client import QdrantClient, models

from app.core.config import QDRANT_API_KEY, QDRANT_URL
from rag.vector_store import VECTOR_STORE_PATH, COLLECTION_NAME


def main():
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("Qdrant Cloud configuration is missing.")

    local = QdrantClient(path=str(VECTOR_STORE_PATH))
    cloud = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=60,
    )

    try:
        if cloud.collection_exists(COLLECTION_NAME):
            raise RuntimeError(
                "Cloud collection already exists. "
                "Migration stopped to protect cloud data."
            )

        info = local.get_collection(COLLECTION_NAME)
        vector_config = info.config.params.vectors

        cloud.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=vector_config,
        )

        offset = None
        total = 0

        while True:
            points, offset = local.scroll(
                collection_name=COLLECTION_NAME,
                limit=50,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )

            if not points:
                break

            cloud.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=point.id,
                        vector=point.vector,
                        payload=point.payload,
                    )
                    for point in points
                ],
                wait=True,
            )

            total += len(points)
            print(f"Copied {total} points...")

            if offset is None:
                break

        cloud_info = cloud.get_collection(COLLECTION_NAME)

        print("Migration completed.")
        print("Local points:", info.points_count)
        print("Cloud points:", cloud_info.points_count)

        if cloud_info.points_count != info.points_count:
            raise RuntimeError(
                "Point counts differ. Keep the local collection unchanged "
                "and investigate before proceeding."
            )

    finally:
        local.close()
        cloud.close()


if __name__ == "__main__":
    main()
