from pathlib import Path
import sys


def main() -> None:
    if len(sys.argv) != 8:
        raise SystemExit(
            "Usage: rewrite_manifest.py "
            "<manifest> "
            "<argocd-source> <argocd-target> "
            "<dex-source> <dex-target> "
            "<redis-source> <redis-target>"
        )

    path = Path(sys.argv[1])

    replacements = {
        sys.argv[2]: sys.argv[3],
        sys.argv[4]: sys.argv[5],
        sys.argv[6]: sys.argv[7],
    }

    text = path.read_text(encoding="utf-8")

    for source, target in replacements.items():
        count = text.count(source)

        if count == 0:
            raise SystemExit(
                f"Expected image reference not found: {source}"
            )

        print(
            f"{source}: replacing {count} occurrence(s)"
        )

        text = text.replace(
            source,
            target,
        )

    path.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Private-ECR Argo CD manifest generated successfully."
    )


if __name__ == "__main__":
    main()