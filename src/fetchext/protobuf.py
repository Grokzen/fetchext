from typing import Dict, List, Tuple

class SimpleProtobuf:
    """
    A minimal Protobuf decoder for CRX3 headers.
    Only supports Length-Delimited (Type 2) fields.
    """
    
    @staticmethod
    def parse(data: bytes) -> Dict[int, List[bytes]]:
        """
        Parses protobuf data and returns a dict of field_id -> list of values (bytes).
        """
        result = {}
        i = 0
        n = len(data)
        
        while i < n:
            # Read key (varint)
            key, new_i = SimpleProtobuf._read_varint(data, i)
            i = new_i
            
            wire_type = key & 0x07
            field_id = key >> 3
            
            if wire_type != 2:
                # We only expect Length Delimited (2) for CRX3 header fields
                # If we encounter others, we might need to skip them, but for now let's raise or break
                # To skip, we need to know how to parse other types.
                # Varint (0): read varint
                # 64-bit (1): skip 8 bytes
                # 32-bit (5): skip 4 bytes
                if wire_type == 0:
                    _, i = SimpleProtobuf._read_varint(data, i)
                elif wire_type == 1:
                    i += 8
                elif wire_type == 5:
                    i += 4
                else:
                    raise ValueError(f"Unsupported wire type: {wire_type}")
                continue
                
            # Read length (varint)
            length, new_i = SimpleProtobuf._read_varint(data, i)
            i = new_i
            
            # Read value
            value = data[i : i + length]
            i += length
            
            if field_id not in result:
                result[field_id] = []
            result[field_id].append(value)
            
        return result

    @staticmethod
    def _read_varint(data: bytes, offset: int) -> Tuple[int, int]:
        """Reads a varint from data at offset. Returns (value, new_offset)."""
        value = 0
        shift = 0
        while True:
            if offset >= len(data):
                raise ValueError("Unexpected end of data while reading varint")
            byte = data[offset]
            offset += 1
            value |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return value, offset
