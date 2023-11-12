#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
The Game Boy uses tiles as the building block for all graphics on the screen. This base-class is used both for
`pyboy.api.sprite.Sprite` and `pyboy.api.tilemap.TileMap`, when refering to graphics.
"""

import numpy as np

import pyboy

from .constants import LOW_TILEDATA, VRAM_OFFSET

logger = pyboy.logging.get_logger(__name__)

try:
    from PIL import Image
except ImportError:
    Image = None


class Tile:
    def __init__(self, mb, identifier):
        """
        The Game Boy uses tiles as the building block for all graphics on the screen. This base-class is used for
        `pyboy.tile`, `pyboy.api.sprite.Sprite` and `pyboy.api.tilemap.TileMap`, when refering to graphics.

        This class is not meant to be instantiated by developers reading this documentation, but it will be created
        internally and returned by `pyboy.api.sprite.Sprite.tiles` and
        `pyboy.api.tilemap.TileMap.tile`.

        The data of this class is static, apart from the image data, which is loaded from the Game Boy's memory when
        needed. Beware that the graphics for the tile can change between each call to `pyboy.PyBoy.tick`.
        """
        self.mb = mb

        assert 0 <= identifier < 384, "Identifier out of range"

        self.data_address = LOW_TILEDATA + (16*identifier)
        """
        The tile data is defined in a specific area of the Game Boy. This function returns the address of the tile data
        corresponding to the tile identifier. It is advised to use `pyboy.api.tile.Tile.image` or one of the
        other `image`-functions if you want to view the tile.

        You can read how the data is read in the
        [Pan Docs: VRAM Tile Data](http://bgb.bircd.org/pandocs.htm#vramtiledata).

        Returns
        -------
        int:
            address in VRAM where tile data starts
        """

        self.tile_identifier = (self.data_address - LOW_TILEDATA) // 16
        """
        The Game Boy has a slightly complicated indexing system for tiles. This identifier unifies the otherwise
        complicated indexing system on the Game Boy into a single range of 0-383 (both included).

        Returns
        -------
        int:
            Unique identifier for the tile
        """

        self.shape = (8, 8)
        """
        Tiles are always 8x8 pixels.

        Returns
        -------
        (int, int):
            The width and height of the tile.
        """

    def image(self):
        """
        Use this function to get an easy-to-use `PIL.Image` object of the tile. The image is 8x8 pixels in RGBA colors.

        Be aware, that the graphics for this tile can change between each call to `pyboy.PyBoy.tick`.

        Returns
        -------
        PIL.Image :
            Image of tile in 8x8 pixels and RGBA colors.
        """
        if Image is None:
            logger.error(f"{__name__}: Missing dependency \"Pillow\".")
            return None
        return Image.frombytes("RGBA", (8, 8), bytes(self.image_data()))

    def image_ndarray(self):
        """
        Use this function to get an easy-to-use `numpy.ndarray` object of the tile. The array has a shape of (8, 8, 4)
        and each value is of `numpy.uint8`. The values corresponds to and RGBA image of 8x8 pixels with each sub-color
        in a separate cell.

        Be aware, that the graphics for this tile can change between each call to `pyboy.PyBoy.tick`.

        Returns
        -------
        numpy.ndarray :
            Array of shape (8, 8, 4) with data type of `numpy.uint8`.
        """
        return np.asarray(self.image_data()).view(dtype=np.uint8).reshape(8, 8, 4)

    def image_data(self):
        """
        Use this function to get the raw tile data. The data is a `memoryview` corresponding to 8x8 pixels in RGBA
        colors.

        Be aware, that the graphics for this tile can change between each call to `pyboy.PyBoy.tick`.

        Returns
        -------
        memoryview :
            Image data of tile in 8x8 pixels and RGBA colors.
        """
        return self.pyboy._image_data()

    def __eq__(self, other):
        return self.data_address == other.data_address

    def __repr__(self):
        return f"Tile: {self.tile_identifier}"