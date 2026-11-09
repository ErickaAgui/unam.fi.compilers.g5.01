"""Pruebas del formato del árbol y de su exportación, sin abrir Tkinter."""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from Parser import ParseTreeNode
from ParseTreeViewer import tree_layout, export_svg, export_raster


class TreeExportTests(unittest.TestCase):
    def setUp(self):
        self.tree = ParseTreeNode("program", [
            ParseTreeNode("statement", [ParseTreeNode("INTEGER -> '10'")]),
            ParseTreeNode("EOF"),
        ])

    def test_tree_layout_hides_eof_only_in_visual_output(self):
        layout = tree_layout(self.tree)
        labels = [item[2] for item in layout[0]]
        self.assertIn("program", labels)
        self.assertIn("INTEGER -> '10'", labels)
        self.assertNotIn("EOF", labels)
        self.assertIn("EOF", self.tree.pretty())

    def test_export_svg(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "tree.svg"
            export_svg(str(path), tree_layout(self.tree))
            self.assertIn("<svg", path.read_text(encoding="utf-8"))

    def test_export_png_jpg_and_replace_existing_file(self):
        from PIL import Image
        layout = tree_layout(self.tree)
        with TemporaryDirectory() as folder:
            for name,fmt in (("tree.png", "PNG"), ("tree.jpg", "JPEG")):
                path = Path(folder) / name
                export_raster(str(path), layout, fmt)
                export_raster(str(path), layout, fmt)  # mismo nombre
                with Image.open(path) as img:
                    self.assertEqual(img.format, fmt)
                    self.assertGreater(img.width, 0)
                    self.assertGreater(img.height, 0)
