import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetchext.cli import get_parser
from argparse_manpage.manpage import Manpage

def main():
    parser = get_parser()
    
    # Man page metadata
    man = Manpage(parser)
    man.prog = "fext"
    man.ext_description = "Download and manage browser extensions from the command line."
    man.ext_homepage = "https://github.com/grok/fetchext"
    man.ext_author = "Grok"
    man.ext_section = 1
    
    output_dir = Path("docs/man")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "fext.1"
    with open(output_file, "w") as f:
        f.write(str(man))
        
    print(f"Man page generated at {output_file}")

if __name__ == "__main__":
    main()
