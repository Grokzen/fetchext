import sys
from pathlib import Path
import shtab

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetchext.cli import get_parser


def main():
    parser = get_parser()

    output_dir = Path("docs/completions")
    output_dir.mkdir(parents=True, exist_ok=True)

    shells = ["bash", "zsh"]

    for shell in shells:
        output_file = output_dir / f"fext.{shell}"
        print(f"Generating {shell} completion to {output_file}...")

        completion = shtab.complete(parser, shell=shell)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(completion)


if __name__ == "__main__":
    main()
