from pathlib import Path
from typing import List
from rich.tree import Tree
from rich.markup import escape


def build_file_tree(file_list: List[str], root_name: str) -> Tree:
    """
    Builds a rich Tree from a list of file paths.
    """
    tree = Tree(f":open_file_folder: [bold blue]{escape(root_name)}[/bold blue]")

    # Sort files to ensure folders come before files or alphabetical order
    # Actually, usually folders are grouped. Let's just sort alphabetically.
    file_list.sort()

    # We need to build a nested structure.
    # A simple way is to keep a map of path -> tree_node

    # But since we just want to display, we can process them.
    # Let's use a recursive approach or a dictionary to build the structure first.

    structure = {}

    for filepath in file_list:
        parts = Path(filepath).parts
        current_level = structure
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    # Now convert structure to Tree
    def add_to_tree(node: Tree, current_structure: dict):
        # Sort keys: folders first? or just alphabetical?
        # Let's do alphabetical.
        for name in sorted(current_structure.keys()):
            sub_structure = current_structure[name]
            if sub_structure:
                # It's a folder (or has children)
                branch = node.add(
                    f":file_folder: [bold blue]{escape(name)}[/bold blue]"
                )
                add_to_tree(branch, sub_structure)
            else:
                # It's a file (leaf in our structure dict, though technically empty dict)
                # Wait, if it's a file, sub_structure is empty dict.
                # But a folder can also be empty.
                # In a zip, usually we get full paths. 'a/b.txt'.
                # 'a' will be in structure. 'b.txt' will be in 'a'.
                # 'b.txt' points to {}.
                # How do we distinguish empty folder from file?
                # ZipFile.namelist() usually includes directories with trailing slash if they are explicit.
                # But implicit directories might not be there.
                # Let's assume if it has no children in our structure, it's a file?
                # No, 'a/b/' could be an empty dir.
                # Let's look at the original list.
                pass

    # Re-thinking: The structure dict doesn't distinguish files/folders well if we just use {} for everything.
    # Let's just use the path parts.

    # Better approach:
    # Iterate over sorted paths.
    # Maintain a cache of created nodes for directory paths.

    node_cache = {".": tree}

    for filepath in file_list:
        path = Path(filepath)
        parts = path.parts

        parent_path = "."
        for i, part in enumerate(parts):
            current_path_str = str(Path(*parts[: i + 1]))
            is_last = i == len(parts) - 1

            # If this is a directory entry in the zip (ends with /), handle it.
            # ZipFile.namelist() entries ending in / are directories.
            # But we stripped that when using Path.parts? Path('a/') parts is ('a',).

            # Let's rely on the input string.
            original_path = filepath
            is_directory_entry = original_path.endswith("/")

            if current_path_str not in node_cache:
                parent_node = node_cache[parent_path]

                if is_last and not is_directory_entry:
                    # It's a file
                    parent_node.add(f":page_facing_up: {escape(part)}")
                else:
                    # It's a directory (either explicit or implicit parent)
                    branch = parent_node.add(
                        f":file_folder: [bold blue]{escape(part)}[/bold blue]"
                    )
                    node_cache[current_path_str] = branch

            parent_path = current_path_str

    return tree
