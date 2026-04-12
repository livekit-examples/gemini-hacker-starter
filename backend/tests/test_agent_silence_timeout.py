import pytest

from app import agent_main


class _FakeParticipant:
    def __init__(self, audio_level: float) -> None:
        self.audio_level = audio_level


class _FakeRoom:
    def __init__(self, active_speakers=None, remote_participants=None) -> None:
        self.active_speakers = active_speakers or []
        self.remote_participants = remote_participants or {}


@pytest.mark.parametrize(
    "room, threshold, expected",
    [
        (_FakeRoom(active_speakers=[_FakeParticipant(0.25)]), 0.02, True),
        (
            _FakeRoom(
                active_speakers=[],
                remote_participants={"u1": _FakeParticipant(0.10)},
            ),
            0.05,
            True,
        ),
        (
            _FakeRoom(
                active_speakers=[_FakeParticipant(0.01)],
                remote_participants={"u1": _FakeParticipant(0.01)},
            ),
            0.05,
            False,
        ),
    ],
)
def test_has_remote_speech_activity(room, threshold, expected):
    assert agent_main._has_remote_speech_activity(room, threshold) is expected


@pytest.mark.asyncio
async def test_shutdown_due_to_silence_uses_job_context_shutdown_first():
    called = []

    class _Ctx:
        class _Room:
            async def disconnect(self):
                called.append("room.disconnect")

        room = _Room()

        async def shutdown(self):
            called.append("ctx.shutdown")

    class _Session:
        async def close(self):
            called.append("session.close")

    await agent_main._shutdown_due_to_silence(_Ctx(), _Session())

    assert called == ["ctx.shutdown"]


@pytest.mark.asyncio
async def test_shutdown_due_to_silence_falls_back_to_session_close():
    called = []

    class _Ctx:
        class _Room:
            async def disconnect(self):
                called.append("room.disconnect")

        room = _Room()

    class _Session:
        async def close(self):
            called.append("session.close")

    await agent_main._shutdown_due_to_silence(_Ctx(), _Session())

    assert called == ["session.close"]
