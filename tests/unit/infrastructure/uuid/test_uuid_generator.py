import pytest
from pytest_mock import MockerFixture
from uuid import UUID

from src.infrastructure.uuid.uuid_generator import UUIDv7Generator

class TestUUIDv7Generator:
    @pytest.fixture
    def generator(self) -> UUIDv7Generator:
        return UUIDv7Generator()

    def test_uuid_generation_with_fixed_values(
        self,
        generator: UUIDv7Generator,
        mocker: MockerFixture
    ):
        """UUID 생성이 명세에 맞게 이루어지는지 검증합니다.
        
        UUID v7의 구조:
        - 처음 48비트: 타임스탬프
        - 다음 4비트: 버전(7)
        - 다음 2비트: variant(2)
        - 나머지: 랜덤 값
        """
        # Given
        fixed_time = 1710672000.0  # 2024-03-17 12:00:00
        mocker.patch('time.time', return_value=fixed_time)
        
        fixed_random = 0x123456  # 테스트용 랜덤 값
        mocker.patch('random.getrandbits', return_value=fixed_random)

        # When
        result = generator.generate()

        # Then
        # 타임스탬프 부분 검증 (상위 48비트)
        timestamp_ms = int(fixed_time * 1000)
        expected_timestamp = (result.int >> 80) & ((1 << 48) - 1)
        assert expected_timestamp == timestamp_ms & ((1 << 48) - 1)

        # 버전 비트 검증 (버전 7)
        version = (result.int >> 76) & 0xF
        assert version == 0x7

        # Variant 비트 검증 (RFC 4122: 2)
        variant = (result.int >> 62) & 0x3
        assert variant == 0x2

    def test_sequential_generation(
        self,
        generator: UUIDv7Generator,
        mocker: MockerFixture
    ):
        """연속 생성된 UUID가 시간 순서를 유지하는지 검증합니다."""
        # Given
        timestamps = [1710672000.0 + i/1000 for i in range(5)]
        mock_time = mocker.patch('time.time')
        mock_time.side_effect = timestamps
        
        mocker.patch('random.getrandbits', return_value=0)

        # When
        uuids = [generator.generate() for _ in range(5)]

        # Then
        # 시간 순서대로 정렬되어 있는지 확인
        assert uuids == sorted(uuids)
        # 모든 UUID가 고유한지 확인
        assert len(set(uuids)) == len(uuids)

    def test_version_and_variant_bits(
        self,
        generator: UUIDv7Generator,
        mocker: MockerFixture
    ):
        """UUID의 버전과 variant 비트가 올바르게 설정되는지 검증합니다."""
        # Given
        mocker.patch('time.time', return_value=1710672000.0)
        mocker.patch('random.getrandbits', return_value=0)

        # When
        result = generator.generate()

        # Then
        # 버전 비트 검증 (4비트)
        version = (result.int >> 76) & 0xF
        assert version == 0x7, f"잘못된 버전 비트: {version:x}, 예상값: 7"

        # Variant 비트 검증 (2비트)
        variant = (result.int >> 62) & 0x3
        assert variant == 0x2, f"잘못된 variant 비트: {variant:x}, 예상값: 2"