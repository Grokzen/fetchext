from rich.tree import Tree
from fetchext.preview import build_file_tree


def test_build_file_tree_simple():
    files = ["manifest.json", "background.js"]
    tree = build_file_tree(files, "root")

    assert isinstance(tree, Tree)
    assert str(tree.label) == ":open_file_folder: [bold blue]root[/bold blue]"

    # Rich tree structure is complex to assert exactly on string representation
    # but we can check children count
    assert len(tree.children) == 2


def test_build_file_tree_nested():
    files = ["manifest.json", "js/background.js", "js/content.js", "css/style.css"]
    tree = build_file_tree(files, "root")

    assert len(tree.children) == 3  # manifest.json, js/, css/

    # Find js folder
    js_node = None
    for child in tree.children:
        if "js" in str(child.label):
            js_node = child
            break

    assert js_node is not None
    assert len(js_node.children) == 2  # background.js, content.js


def test_build_file_tree_deep_nesting():
    files = ["a/b/c/d.txt"]
    tree = build_file_tree(files, "root")

    current = tree
    path = ["a", "b", "c", "d.txt"]

    for part in path:
        assert len(current.children) == 1
        current = current.children[0]
        assert part in str(current.label)


def test_build_file_tree_with_directory_entries():
    # Zip files sometimes include directory entries ending in /
    files = ["folder/", "folder/file.txt"]
    tree = build_file_tree(files, "root")

    assert len(tree.children) == 1
    folder_node = tree.children[0]
    assert "folder" in str(folder_node.label)
    assert len(folder_node.children) == 1
    assert "file.txt" in str(folder_node.children[0].label)
