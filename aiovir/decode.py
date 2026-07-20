"""
AES-GCM + MessagePack decoder/encoder for Virasty API protocol.
"""

import os
import re
import struct
import base64
from pathlib import Path
from typing import Any, Dict, Union, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import msgpack


class VirastyDecoder:
    """
    AES-128-GCM encryption/decryption for Virasty API.
    
    Key: First 16 bytes of DUID
    IV: First 12 bytes of ciphertext
    Format: MessagePack (map16 for dicts, matching browser)
    
    DUID stored in ~/.aiovir/duid
    Default: 1jtbfnd001f4je-web
    """

    DEFAULT_DUID = "1jtbfnd001f4je-web"
    CONFIG_DIR = Path.home() / ".aiovir"
    DUID_FILE = CONFIG_DIR / "duid"
    
    ACTION_MAP = {
        "sendByMobile": "login",
    }

    def __init__(self, duid: Optional[str] = None):
        self._duid = None
        self._key = None
        self._aesgcm = None
        
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        if duid:
            self.set_duid(duid)
        else:
            self._load_duid()

    def _load_duid(self) -> None:
        if self.DUID_FILE.exists():
            duid = self.DUID_FILE.read_text().strip()
            if duid:
                self.set_duid(duid)
                return
        self.set_duid(self.DEFAULT_DUID)

    def _save_duid(self, duid: str) -> None:
        self.DUID_FILE.write_text(duid)

    @property
    def duid(self) -> Optional[str]:
        return self._duid

    def set_duid(self, duid: str) -> None:
        self._duid = duid
        key_bytes = duid[:16].encode('utf-8')
        if len(key_bytes) < 16:
            key_bytes = key_bytes.ljust(16, b'\x00')
        self._key = key_bytes
        self._aesgcm = AESGCM(self._key)
        self._save_duid(duid)

    def _ensure_ready(self) -> None:
        if self._aesgcm is None:
            raise RuntimeError("DUID not set")

    @staticmethod
    def _pack_string(s: str) -> bytes:
        b = s.encode('utf-8')
        length = len(b)
        if length <= 31:
            return bytes([0xa0 + length]) + b
        elif length <= 255:
            return b'\xd9' + bytes([length]) + b
        else:
            return b'\xda' + struct.pack('>H', length) + b

    @staticmethod
    def _pack_value(v: Any) -> bytes:
        if isinstance(v, str):
            return VirastyDecoder._pack_string(v)
        elif isinstance(v, dict):
            return VirastyDecoder._pack_map(v)
        elif isinstance(v, bool):
            return b'\xc3' if v else b'\xc2'
        elif v is None:
            return b'\xc0'
        elif isinstance(v, int):
            if 0 <= v <= 127:
                return bytes([v])
            elif -32 <= v <= -1:
                return bytes([v & 0xff])
            elif v <= 255:
                return b'\xcc' + bytes([v])
            elif v <= 65535:
                return b'\xcd' + struct.pack('>H', v)
            else:
                return b'\xce' + struct.pack('>I', v)
        elif isinstance(v, float):
            return b'\xcb' + struct.pack('>d', v)
        elif isinstance(v, bytes):
            length = len(v)
            if length <= 255:
                return b'\xc4' + bytes([length]) + v
            else:
                return b'\xc5' + struct.pack('>H', length) + v
        elif isinstance(v, list):
            return VirastyDecoder._pack_array(v)
        else:
            return VirastyDecoder._pack_string(str(v))

    @staticmethod
    def _pack_map(d: Dict) -> bytes:
        result = b'\xde' + struct.pack('>H', len(d))
        for k, v in d.items():
            result += VirastyDecoder._pack_string(k)
            result += VirastyDecoder._pack_value(v)
        return result

    @staticmethod
    def _pack_array(arr: list) -> bytes:
        if len(arr) <= 15:
            result = bytes([0x90 + len(arr)])
        else:
            result = b'\xdc' + struct.pack('>H', len(arr))
        for item in arr:
            result += VirastyDecoder._pack_value(item)
        return result

    def _pack(self, data: Any) -> bytes:
        return self._pack_value(data)

    def _to_bytes(self, data: Union[str, bytes, list, bytearray]) -> bytes:
        if isinstance(data, (bytes, bytearray)):
            return bytes(data)
        
        if isinstance(data, list):
            return bytes(data)
        
        if isinstance(data, str):
            data = data.strip()
            
            duid_match = re.search(r"-H\s+['\"]duid:\s*([^\s'\"]+)['\"]", data)
            if duid_match and ('curl' in data.lower() or 'api.virasty.com' in data):
                extracted_duid = duid_match.group(1)
                self.set_duid(extracted_duid)
                raise ValueError(
                    f"DUID extracted and saved: {extracted_duid}\n"
                    f"Please retry with the actual encrypted data."
                )
            
            cleaned = data.replace('-', '+').replace('_', '/')
            remainder = len(cleaned) % 4
            if remainder:
                cleaned += '=' * (4 - remainder)
            return base64.b64decode(cleaned)
        
        raise TypeError(f"Unsupported data type: {type(data)}")

    def decrypt(self, encrypted_data: Union[str, bytes, list]) -> Any:
        self._ensure_ready()
        
        data = self._to_bytes(encrypted_data)
        
        iv = data[:12]
        ciphertext = data[12:]
        
        plaintext = self._aesgcm.decrypt(iv, ciphertext, None)
        return msgpack.unpackb(plaintext, raw=False)

    def decrypt_response(self, response_data: Union[str, bytes]) -> Any:
        return self.decrypt(response_data)

    def encrypt(self, data: Any) -> bytes:
        self._ensure_ready()
        
        packed = self._pack(data)
        iv = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(iv, packed, None)
        
        return iv + ciphertext

    def encrypt_to_b64(self, data: Any) -> str:
        return base64.b64encode(self.encrypt(data)).decode('ascii')

    def decrypt_b64(self, b64_string: str) -> Any:
        return self.decrypt(b64_string)

    def encrypt_request(self, endpoint: str, payload: Dict[str, Any]) -> bytes:
        raw_action = endpoint.rsplit("/", 1)[-1]
        action = self.ACTION_MAP.get(raw_action, raw_action)
        
        body = {"action": action, **payload}
        return self.encrypt(body)

    @staticmethod
    def decrypt_with(encrypted_data: Union[str, bytes], duid: str) -> Any:
        decoder = VirastyDecoder(duid)
        return decoder.decrypt(encrypted_data)

    @staticmethod
    def encrypt_with(data: Any, duid: str) -> str:
        decoder = VirastyDecoder(duid)
        return decoder.encrypt_to_b64(data)