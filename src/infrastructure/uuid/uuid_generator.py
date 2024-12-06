import random
import time
from uuid import UUID


class UUIDv7Generator:
    def generate(self) -> UUID:
        """UUID v7을 생성합니다.
        
        UUID v7 형식:
        - 처음 48비트: Unix 타임스탬프(밀리초)
        - 다음 4비트: 버전(7)
        - 다음 2비트: variant(2)
        - 나머지 비트: 무작위 값
        """
        # 현재 시간을 밀리초로 변환
        timestamp_ms = int(time.time() * 1000)
        
        # 무작위 비트 생성 (74비트 필요)
        rand_bits = random.getrandbits(74)
        
        # UUID 정수 생성
        uuid_int = 0
        
        # 상위 48비트에 타임스탬프 설정
        uuid_int |= (timestamp_ms & ((1 << 48) - 1)) << 80
        
        # 버전 7 설정 (다음 4비트)
        uuid_int |= 0x7 << 76
        
        # Variant 2 설정 (다음 2비트)
        uuid_int |= 0x2 << 62
        
        # 나머지 비트를 랜덤값으로 채움
        uuid_int |= rand_bits & ((1 << 62) - 1)
        
        return UUID(int=uuid_int)