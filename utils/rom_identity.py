"""ROM identity helpers used to validate code targets before patching."""

from dataclasses import dataclass
import hashlib
from pathlib import Path


PP64_BASE_ROMS = {
    "mp1": "8BC2712139FBF0C56C8EA835802C52DC",
    "mp2": "04840612A35ECE222AFDB2DFBF926409",
    "mp3": "76A8BBC81BC2060EC99C9645867237CC",
}


@dataclass(frozen=True)
class RomIdentity:
    path: Path
    size: int
    md5: str
    sha256: str
    byte_order: str
    internal_name: str
    region: str
    version: int

    @property
    def pp64_game(self):
        for game, digest in PP64_BASE_ROMS.items():
            if self.md5 == digest:
                return game
        return None


def _digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def inspect_n64(path) -> RomIdentity:
    path = Path(path).expanduser().resolve()
    with path.open("rb") as stream:
        header = stream.read(0x40)
    if len(header) < 0x40:
        raise ValueError("File is too small to be an N64 ROM")

    magic = header[:4]
    byte_orders = {b"\x80\x37\x12\x40": "z64", b"\x37\x80\x40\x12": "v64", b"\x40\x12\x37\x80": "n64"}
    if magic not in byte_orders:
        raise ValueError("File does not have a recognized N64 byte order")

    region_byte = header[0x3E]
    region = chr(region_byte) if 32 <= region_byte < 127 else f"0x{region_byte:02X}"
    return RomIdentity(
        path=path,
        size=path.stat().st_size,
        md5=_digest(path, "md5"),
        sha256=_digest(path, "sha256"),
        byte_order=byte_orders[magic],
        internal_name=header[0x20:0x34].rstrip(b"\0 ").decode("ascii", errors="replace"),
        region=region,
        version=header[0x3F],
    )


def pp64_target_status(path, game: str):
    """Return a conservative status; edited PP64 ROMs are derivatives, not bases."""
    identity = inspect_n64(path)
    expected = PP64_BASE_ROMS.get(game.lower())
    if expected is None:
        raise ValueError(f"Unknown PP64 game target: {game}")
    if identity.md5 == expected:
        return identity, "supported-base"
    return identity, "edited-or-unrecognized"
